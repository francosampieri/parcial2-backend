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
