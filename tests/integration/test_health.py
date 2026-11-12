"""Health se verifica únicamente tras startup realmente ejecutado."""
import pytest
from sqlalchemy import event


@pytest.mark.asyncio
@pytest.mark.parametrize("database_down", [False, True])
async def test_live_sin_sql_ni_sesion_incluso_con_caida(application, client, postgres_cluster, monkeypatch, database_down):
    statements = []
    def observe(*args):
        statements.append(args[2])
    def forbidden_factory():
        pytest.fail("live no debe crear una sesión")
    event.listen(application.state.engine.sync_engine, "before_cursor_execute", observe)
    monkeypatch.setattr(application.state, "session_factory", forbidden_factory)
    if database_down:
        postgres_cluster.stop()
    try:
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"estado": "vivo"}
        assert statements == []
    finally:
        if database_down:
            postgres_cluster.start()
        event.remove(application.state.engine.sync_engine, "before_cursor_execute", observe)

@pytest.mark.asyncio
@pytest.mark.parametrize("requests_count", [1, 3])
async def test_ready_consulta_nueva_y_cierra_sesion(application, client, requests_count):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    closed = []
    statements = []
    class TrackedSession(AsyncSession):
        async def close(self):
            await super().close()
            closed.append(self)
    application.state.session_factory = async_sessionmaker(application.state.engine, class_=TrackedSession, expire_on_commit=False)
    def observe(*args):
        statements.append(args[2])
    event.listen(application.state.engine.sync_engine, "before_cursor_execute", observe)
    try:
        for _ in range(requests_count):
            response = await client.get("/health/ready")
            assert response.status_code == 200
            assert response.json() == {"estado": "listo"}
        assert statements == ["SELECT 1"] * requests_count
        assert len(closed) == requests_count
        assert len({id(session) for session in closed}) == requests_count
        assert application.state.engine.pool.checkedout() == 0
    finally:
        event.remove(application.state.engine.sync_engine, "before_cursor_execute", observe)

@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["conexion", "consulta"])
async def test_ready_traduce_caida_y_permite_recuperacion(application, client, failure):
    from unittest.mock import AsyncMock
    from sqlalchemy.exc import OperationalError
    from app.core.database import get_session
    error = ConnectionRefusedError("SECRETO de conexión") if failure == "conexion" else OperationalError("SELECT PRIVADO", {}, Exception("SECRETO de consulta"))
    session = AsyncMock()
    session.execute.side_effect = [error, None]
    async def override_session():
        try:
            yield session
        finally:
            await session.close()
    application.dependency_overrides[get_session] = override_session
    failed = await client.get("/health/ready")
    assert failed.status_code == 503
    assert failed.json() == {"detail": "Base de datos no disponible"}
    assert session.close.await_count == 1
    recovered = await client.get("/health/ready")
    assert recovered.status_code == 200
    assert recovered.json() == {"estado": "listo"}
    assert session.execute.await_count == session.close.await_count == 2


@pytest.mark.asyncio
async def test_ready_no_oculta_errores_de_programacion(application, client):
    from unittest.mock import AsyncMock
    from sqlalchemy.exc import ProgrammingError
    from app.core.database import get_session
    session = AsyncMock()
    session.execute.side_effect = ProgrammingError("SQL inválido del programador", {}, Exception("programación"))
    async def override_session():
        try:
            yield session
        finally:
            await session.close()
    application.dependency_overrides[get_session] = override_session
    with pytest.raises(ProgrammingError):
        await client.get("/health/ready")
    session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_ready_caida_y_recuperacion_real_postgres(application, client, postgres_cluster):
    assert (await client.get("/health/ready")).json() == {"estado": "listo"}
    postgres_cluster.stop()
    try:
        response = await client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Base de datos no disponible"}
        assert (await client.get("/health/live")).json() == {"estado": "vivo"}
        assert application.state.engine.pool.checkedout() == 0
    finally:
        postgres_cluster.start()
    response = await client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"estado": "listo"}

@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["fabrica", "entrada"])
async def test_ready_fallo_antes_de_handler_y_recuperacion(application, client, phase):
    from contextlib import asynccontextmanager
    from sqlalchemy.exc import OperationalError
    original = application.state.session_factory
    cleaned = []
    @asynccontextmanager
    async def unavailable_context():
        try:
            raise OperationalError("SQL PRIVADO", {}, Exception("SECRETO"))
            yield
        finally:
            cleaned.append(True)
    def unavailable_factory():
        if phase == "fabrica":
            raise ConnectionRefusedError("SECRETO")
        return unavailable_context()
    application.state.session_factory = unavailable_factory
    try:
        response = await client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Base de datos no disponible"}
        assert cleaned == ([True] if phase == "entrada" else [])
        assert application.state.engine.pool.checkedout() == 0
    finally:
        application.state.session_factory = original
    assert (await client.get("/health/ready")).json() == {"estado": "listo"}


@pytest.mark.asyncio
async def test_factory_error_programacion_no_se_convierte_en_503(application, client, monkeypatch):
    def broken_factory():
        raise RuntimeError("error de programación")
    monkeypatch.setattr(application.state, "session_factory", broken_factory)
    with pytest.raises(RuntimeError, match="error de programación"):
        await client.get("/health/ready")

@pytest.mark.asyncio
@pytest.mark.parametrize("invalidated", [False, True])
async def test_ready_dbapi_desconexion_se_clasifica(application, client, invalidated):
    from unittest.mock import AsyncMock
    from sqlalchemy.exc import DBAPIError
    from app.core.database import get_session
    session = AsyncMock()
    error = DBAPIError("SELECT PRIVADO", {}, Exception("SECRETO DRIVER"), connection_invalidated=invalidated)
    session.execute.side_effect = error
    async def override_session():
        try:
            yield session
        finally:
            await session.close()
    application.dependency_overrides[get_session] = override_session
    if invalidated:
        response = await client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Base de datos no disponible"}
    else:
        with pytest.raises(DBAPIError) as caught:
            await client.get("/health/ready")
        assert caught.value is error
    session.close.assert_awaited_once()
