"""Aceptación del arranque real, sin consultas de dominio."""
import os
from pathlib import Path
import subprocess
import sys

from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
import pytest

from app.main import create_app
from app.core.config import ConfigurationError


@pytest.mark.asyncio
async def test_startup_sin_url_falla():
    with pytest.raises(ConfigurationError):
        async with LifespanManager(create_app()):
            pytest.fail("No debe servir sin configuración")


@pytest.mark.asyncio
async def test_startup_con_postgres_privado(database_url):
    async with LifespanManager(create_app()) as manager:
        async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
            response = await client.get("/openapi.json")
            assert response.status_code == 200
            assert response.json()["info"]["title"] == "Librería — totones"


def test_importar_sin_url_no_abre_red():
    root = Path(__file__).resolve().parents[2]
    environment = os.environ.copy()
    environment.pop("DATABASE_URL", None)
    code = "import socket; socket.socket.connect=lambda *a,**k: (_ for _ in ()).throw(AssertionError('red al importar')); from app.main import app, create_app; assert app is not create_app()"
    result = subprocess.run([sys.executable, "-c", code], cwd=root, env=environment, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    assert result.returncode == 0, result.stderr

@pytest.mark.asyncio
async def test_instancias_poseen_motor_y_fabrica_independientes(database_url):
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncEngine
    first, second = create_app(), create_app()
    async with LifespanManager(first), LifespanManager(second):
        assert isinstance(first.state.engine, AsyncEngine)
        assert first.state.engine is not second.state.engine
        assert first.state.session_factory is not second.state.session_factory
        async with first.state.session_factory() as session:
            assert session.sync_session.expire_on_commit is False
            assert (await session.execute(text("SELECT current_database()"))).scalar_one() == "libreria_test"


@pytest.mark.asyncio
async def test_startup_conexion_rechazada_es_error_sanitizado(monkeypatch):
    import socket
    from app.core.database import DatabaseUnavailableError
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    monkeypatch.setenv("DATABASE_URL", f"postgresql+asyncpg://ficticio:SECRETO@127.0.0.1:{port}/ausente")
    with pytest.raises(DatabaseUnavailableError) as error:
        async with LifespanManager(create_app()):
            pytest.fail("Startup fallido no debe llegar a servir")
    assert str(error.value) == "Base de datos no disponible"
    assert error.value.__cause__ is None
    assert error.value.__suppress_context__ is True

@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [None, "conexion", "inicializacion", "fabrica"])
async def test_motor_dispuesto_tras_cierre_o_fallo(database_url, monkeypatch, failure):
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError
    from app import main
    from app.core.database import DatabaseUnavailableError
    original_engine = main.create_async_engine
    disposed = []
    def tracked_engine(*args, **kwargs):
        engine = original_engine(*args, **kwargs)
        event.listen(engine.sync_engine, "engine_disposed", lambda _: disposed.append(engine))
        return engine
    monkeypatch.setattr(main, "create_async_engine", tracked_engine)
    if failure == "fabrica":
        def fail_factory(*args, **kwargs):
            raise RuntimeError("fallo propio de programación")
        monkeypatch.setattr(main, "async_sessionmaker", fail_factory)
    elif failure:
        async def fail_initialize(engine):
            if failure == "conexion":
                raise OperationalError("SQL PRIVADO", {}, Exception("SECRETO"))
            raise RuntimeError("fallo propio de programación")
        monkeypatch.setattr(main, "initialize_database", fail_initialize)
    application = create_app()
    if failure:
        expected = DatabaseUnavailableError if failure == "conexion" else RuntimeError
        with pytest.raises(expected) as error:
            async with LifespanManager(application):
                pytest.fail("Startup no debe completarse")
        if failure == "conexion":
            assert str(error.value) == "Base de datos no disponible"
            assert error.value.__suppress_context__
    else:
        async with LifespanManager(application):
            assert not disposed
    assert disposed == [application.state.engine]


@pytest.mark.asyncio
@pytest.mark.parametrize("value,expected", [("false", False), ("TRUE", True)])
async def test_motor_recibe_echo_interpretado(database_url, monkeypatch, value, expected):
    monkeypatch.setenv("SQL_ECHO", value)
    application = create_app()
    async with LifespanManager(application):
        assert application.state.engine.echo is expected

@pytest.mark.asyncio
async def test_startup_base_inexistente_no_expone_error_driver(database_url, monkeypatch):
    from sqlalchemy.engine import make_url
    from app.core.database import DatabaseUnavailableError
    address = make_url(database_url).set(database="foundation_missing")
    monkeypatch.setenv("DATABASE_URL", address.render_as_string(hide_password=False))
    with pytest.raises(DatabaseUnavailableError) as error:
        async with LifespanManager(create_app()):
            pytest.fail("No debe servir con base inexistente")
    assert str(error.value) == "Base de datos no disponible"
    assert error.value.__cause__ is None
    assert error.value.__suppress_context__
