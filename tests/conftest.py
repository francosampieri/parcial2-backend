"""Fixtures compartidas; nunca leer el .env personal en pruebas."""
import pytest


@pytest.fixture(autouse=True)
def controlled_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQL_ECHO", raising=False)

@pytest.fixture(scope="session")
def postgres_cluster():
    from tests.pg_cluster import create_cluster
    cluster = create_cluster()
    try:
        yield cluster
    finally:
        cluster.cleanup()
        print("PostgreSQL privado detenido y directorio propio eliminado")


@pytest.fixture
def database_url(postgres_cluster, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", postgres_cluster.url)
    return postgres_cluster.url

import pytest_asyncio


@pytest_asyncio.fixture
async def application(database_url):
    from asgi_lifespan import LifespanManager
    from app.main import create_app
    instance = create_app()
    async with LifespanManager(instance):
        yield instance


@pytest_asyncio.fixture
async def client(application):
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as instance:
        yield instance

@pytest_asyncio.fixture
async def domain_session(application):
    """Cada prueba usa una transaccion propia que se revierte al salir."""
    from sqlalchemy.ext.asyncio import AsyncSession
    async with application.state.engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(bind=connection, expire_on_commit=False) as session:
            yield session
        if transaction.is_active:
            await transaction.rollback()


@pytest.fixture
def catalog_seed(application):
    """Crear editoriales propias y retirar sólo los identificadores creados."""
    from contextlib import asynccontextmanager
    from sqlalchemy import text

    @asynccontextmanager
    async def group():
        ids = []
        async def create(name):
            async with application.state.engine.begin() as conn:
                result = await conn.execute(text("INSERT INTO editorial (nombre, pais) VALUES (:name, 'AR') RETURNING id"), {"name": name})
                ids.append(result.scalar_one())
        try:
            yield create
        finally:
            async with application.state.engine.begin() as conn:
                for id_ in ids:
                    await conn.execute(text("DELETE FROM editorial WHERE id = :id"), {"id": id_})
    return group


@pytest.fixture
def sale_seed(application):
    """Crear clientes y libros propios; retirar sólo sus ventas y ese catálogo."""
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    import uuid
    from sqlalchemy import text

    @asynccontextmanager
    async def group():
        clientes: list[int] = []
        libros: list[int] = []
        editoriales: list[int] = []

        async def cliente(nombre: str, email: str) -> int:
            async with application.state.engine.begin() as conn:
                result = await conn.execute(
                    text('INSERT INTO cliente (nombre, email) VALUES (:nombre, :email) RETURNING id'),
                    {'nombre': nombre, 'email': email},
                )
                id_ = result.scalar_one()
                clientes.append(id_)
                return id_

        async def libro(titulo: str, precio: str, isbn: str | None = None) -> int:
            if not editoriales:
                async with application.state.engine.begin() as conn:
                    result = await conn.execute(text(
                        "INSERT INTO editorial (nombre, pais) VALUES ('Ventas seed C05', 'AR') RETURNING id"
                    ))
                    editoriales.append(result.scalar_one())
            async with application.state.engine.begin() as conn:
                result = await conn.execute(
                    text('INSERT INTO libro (isbn, titulo, precio, stock, editorial_id) '
                         'VALUES (:isbn, :titulo, :precio, 0, :editorial) RETURNING id'),
                    {'isbn': isbn or f'venta-seed-{uuid.uuid4().hex}', 'titulo': titulo,
                     'precio': precio, 'editorial': editoriales[0]},
                )
                id_ = result.scalar_one()
                libros.append(id_)
                return id_

        try:
            yield SimpleNamespace(cliente=cliente, libro=libro)
        finally:
            async with application.state.engine.begin() as conn:
                if clientes:
                    await conn.execute(text(
                        'DELETE FROM renglon_venta WHERE venta_id IN '
                        '(SELECT id FROM venta WHERE cliente_id = ANY(:ids))'
                    ), {'ids': clientes})
                    await conn.execute(text('DELETE FROM venta WHERE cliente_id = ANY(:ids)'), {'ids': clientes})
                    await conn.execute(text('DELETE FROM perfil_cliente WHERE cliente_id = ANY(:ids)'), {'ids': clientes})
                    await conn.execute(text('DELETE FROM cliente WHERE id = ANY(:ids)'), {'ids': clientes})
                if libros:
                    await conn.execute(text('DELETE FROM libro_autor WHERE libro_id = ANY(:ids)'), {'ids': libros})
                    await conn.execute(text('DELETE FROM libro WHERE id = ANY(:ids)'), {'ids': libros})
                if editoriales:
                    await conn.execute(text('DELETE FROM editorial WHERE id = ANY(:ids)'), {'ids': editoriales})

    return group


@pytest.fixture
def client_seed(application):
    """Sembrar clientes propios y retirar sólo esas filas y sus perfiles."""
    from contextlib import asynccontextmanager
    from sqlalchemy import text

    @asynccontextmanager
    async def group():
        ids: list[int] = []

        async def create(name: str, email: str) -> int:
            async with application.state.engine.begin() as conn:
                result = await conn.execute(
                    text("INSERT INTO cliente (nombre, email) VALUES (:name, :email) RETURNING id"),
                    {"name": name, "email": email},
                )
                id_ = result.scalar_one()
                ids.append(id_)
                return id_

        try:
            yield create
        finally:
            async with application.state.engine.begin() as conn:
                for id_ in ids:
                    await conn.execute(text("DELETE FROM perfil_cliente WHERE cliente_id = :id"), {"id": id_})
                    await conn.execute(text("DELETE FROM cliente WHERE id = :id"), {"id": id_})

    return group
