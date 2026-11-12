"""Metadata local para verificar create_all sin anticipar entidades reales."""
from types import SimpleNamespace
import uuid

from asgi_lifespan import LifespanManager
import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, inspect, text

from app.main import create_app
from app.core import database


@pytest.mark.asyncio
async def test_startup_crea_tabla_registrada_antes_de_servir(database_url, monkeypatch):
    metadata = MetaData()
    table = Table(f"prueba_{uuid.uuid4().hex}", metadata, Column("id", Integer, primary_key=True))
    monkeypatch.setattr(database, "SQLModel", SimpleNamespace(metadata=metadata), raising=False)
    application = create_app()
    async with LifespanManager(application):
        async with application.state.engine.begin() as connection:
            await connection.execute(table.insert().values(id=7))
            assert (await connection.execute(table.select())).scalar_one() == 7
            await connection.run_sync(metadata.drop_all)

@pytest.mark.asyncio
async def test_startup_repetido_conserva_fila_y_estructura(database_url, monkeypatch):
    metadata = MetaData()
    table = Table(f"prueba_{uuid.uuid4().hex}", metadata, Column("id", Integer, primary_key=True), Column("nombre", String(30)))
    monkeypatch.setattr(database, "SQLModel", SimpleNamespace(metadata=metadata))
    first = create_app()
    async with LifespanManager(first):
        async with first.state.engine.begin() as connection:
            await connection.execute(table.insert().values(id=9, nombre="conservar"))
    table.append_column(Column("columna_futura", String(20)))
    second = create_app()
    async with LifespanManager(second):
        async with second.state.engine.begin() as connection:
            row = (await connection.execute(text(f"SELECT id, nombre FROM {table.name}"))).one()
            columns = await connection.run_sync(lambda sync: inspect(sync).get_columns(table.name))
            assert tuple(row) == (9, "conservar")
            assert [column["name"] for column in columns] == ["id", "nombre"]
            await connection.run_sync(metadata.drop_all)


@pytest.mark.asyncio
async def test_registro_antes_de_create_all_y_metadata_global_completa(database_url, monkeypatch):
    from sqlmodel import SQLModel
    order = []
    class ObservedMetadata(MetaData):
        def create_all(self, bind, **kwargs):
            assert order == ["modelos"]
            order.append("create_all")
            super().create_all(bind, **kwargs)
    monkeypatch.setattr(database, "register_models", lambda: order.append("modelos"))
    monkeypatch.setattr(database, "SQLModel", SimpleNamespace(metadata=ObservedMetadata()))
    application = create_app()
    async with LifespanManager(application):
        async with application.state.engine.connect() as connection:
            assert (await connection.execute(text("SELECT 1"))).scalar_one() == 1
    assert order == ["modelos", "create_all"]
    assert set(SQLModel.metadata.tables) == {"editorial", "genero", "autor", "libro", "libro_autor", "cliente", "perfil_cliente", "venta", "renglon_venta"}

@pytest.mark.asyncio
async def test_arranques_conservan_dominio_y_tabla_ajena(database_url):
    from sqlalchemy.ext.asyncio import create_async_engine
    from uuid import uuid4
    token = uuid4().hex
    tabla = f'ajena_{token}'
    engine = create_async_engine(database_url)
    cliente_id = None
    try:
        async with engine.begin() as con:
            await con.execute(text(f'CREATE TABLE {tabla} (id INTEGER PRIMARY KEY, dato TEXT NOT NULL)'))
            await con.execute(text(f"INSERT INTO {tabla} VALUES (1, 'conservar')"))
        primero = create_app()
        async with LifespanManager(primero):
            async with primero.state.engine.begin() as con:
                tablas = await con.run_sync(lambda sync: inspect(sync).get_table_names())
                assert {'editorial','genero','autor','libro','libro_autor','cliente','perfil_cliente','venta','renglon_venta'} <= set(tablas)
                assert 'health' not in tablas
                cliente_id = (await con.execute(text("INSERT INTO cliente(nombre,email) VALUES('prueba',:mail) RETURNING id"), {'mail':token})).scalar_one()
        segundo = create_app()
        async with LifespanManager(segundo):
            async with segundo.state.engine.connect() as con:
                assert (await con.execute(text('SELECT email FROM cliente WHERE id=:id'), {'id':cliente_id})).scalar_one() == token
                assert (await con.execute(text(f'SELECT dato FROM {tabla} WHERE id=1'))).scalar_one() == 'conservar'
                columnas = await con.run_sync(lambda sync: inspect(sync).get_columns(tabla))
                assert [col['name'] for col in columnas] == ['id','dato']
    finally:
        async with engine.begin() as con:
            if cliente_id is not None:
                await con.execute(text('DELETE FROM cliente WHERE id=:id'), {'id':cliente_id})
            await con.execute(text(f'DROP TABLE IF EXISTS {tabla}'))
        await engine.dispose()
