"""Las rutas auxiliares viven sólo en cada app de prueba."""
import asyncio
from typing import Annotated

from fastapi import Depends
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

Session = Annotated[AsyncSession, Depends(get_session)]


@pytest.mark.asyncio
async def test_dos_peticiones_concurrentes_no_comparten_transaccion(application, client):
    sessions = []
    both_entered = asyncio.Event()
    @application.get("/prueba/concurrente")
    async def concurrente(session: Session) -> dict:
        sessions.append(session)
        transaction_id = (await session.execute(text("SELECT txid_current()"))).scalar_one()
        if len(sessions) == 2:
            both_entered.set()
        await asyncio.wait_for(both_entered.wait(), timeout=3)
        return {"transaccion": transaction_id}
    first, second = await asyncio.gather(client.get("/prueba/concurrente"), client.get("/prueba/concurrente"))
    assert first.status_code == second.status_code == 200
    assert sessions[0] is not sessions[1]
    assert first.json()["transaccion"] != second.json()["transaccion"]


@pytest.mark.asyncio
async def test_dependencias_reutilizan_sesion_dentro_de_peticion(application, client):
    def another_dependency(session: Session) -> AsyncSession:
        return session
    @application.get("/prueba/reutilizacion")
    async def reutilizacion(session: Session, other: Annotated[AsyncSession, Depends(another_dependency)]) -> dict:
        return {"misma": session is other}
    assert (await client.get("/prueba/reutilizacion")).json() == {"misma": True}

@pytest.mark.asyncio
@pytest.mark.parametrize("with_error", [False, True])
async def test_cierre_sin_commit_descarta_escrituras(application, client, with_error):
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy import Column, Integer, MetaData, Table, func, select
    from sqlalchemy.ext.asyncio import async_sessionmaker
    import uuid
    closed = []
    class TrackedSession(AsyncSession):
        async def close(self):
            await super().close()
            closed.append(self)
    application.state.session_factory = async_sessionmaker(application.state.engine, class_=TrackedSession, expire_on_commit=False)
    metadata = MetaData()
    table = Table(f"sesion_{uuid.uuid4().hex}", metadata, Column("id", Integer, primary_key=True))
    async with application.state.engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    @application.post("/prueba/sin_commit")
    async def write_without_commit(session: Session) -> dict:
        await session.execute(table.insert().values(id=1))
        if with_error:
            raise RuntimeError("fallo de la ruta auxiliar")
        return {"escrito": True}
    try:
        async with AsyncClient(transport=ASGITransport(app=application, raise_app_exceptions=False), base_url="http://test") as request_client:
            response = await request_client.post("/prueba/sin_commit")
        assert response.status_code == (500 if with_error else 200)
        assert len(closed) == 1
        assert application.state.engine.pool.checkedout() == 0
        async with application.state.engine.connect() as connection:
            assert (await connection.execute(select(func.count()).select_from(table))).scalar_one() == 0
    finally:
        async with application.state.engine.begin() as connection:
            await connection.run_sync(metadata.drop_all)


@pytest.mark.asyncio
@pytest.mark.parametrize("identifier,name", [(1, "primero"), (2, "borde")])
async def test_atributos_disponibles_despues_de_commit(application, identifier, name):
    from sqlalchemy import Column, Integer, MetaData, String, Table, event
    from sqlalchemy.orm import registry
    import uuid
    metadata = MetaData()
    table = Table(f"cargado_{uuid.uuid4().hex}", metadata, Column("id", Integer, primary_key=True), Column("nombre", String(30)))
    mapper = registry(metadata=metadata)
    class Loaded:
        pass
    mapper.map_imperatively(Loaded, table)
    async with application.state.engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    try:
        async with application.state.session_factory() as session:
            row = Loaded()
            row.id, row.nombre = identifier, name
            session.add(row)
            await session.commit()
            sql_after_commit = []
            def observe(*args):
                sql_after_commit.append(args[2])
            event.listen(application.state.engine.sync_engine, "before_cursor_execute", observe)
            try:
                assert (row.id, row.nombre) == (identifier, name)
                assert sql_after_commit == []
            finally:
                event.remove(application.state.engine.sync_engine, "before_cursor_execute", observe)
    finally:
        async with application.state.engine.begin() as connection:
            await connection.run_sync(metadata.drop_all)
        mapper.dispose()
