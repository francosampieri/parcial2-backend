from app.core.config import load_settings


def test_entorno_tiene_prioridad_sobre_dotenv(monkeypatch, tmp_path):
    local = "postgresql+asyncpg://local:ejemplo@localhost/local"
    entorno = "postgresql+asyncpg://entorno:ejemplo@localhost/entorno"
    (tmp_path / ".env").write_text(f"DATABASE_URL={local}\n")
    monkeypatch.setenv("DATABASE_URL", entorno)
    assert load_settings().database_url == entorno

import pytest


def test_solo_dotenv(monkeypatch, tmp_path):
    direccion = "postgresql+asyncpg://local:ejemplo@localhost/local"
    (tmp_path / ".env").write_text(f"DATABASE_URL={direccion}\n")
    assert load_settings().database_url == direccion


@pytest.mark.parametrize("value", [None, "", " ", "malformada:secreto", "sqlite+aiosqlite:///prueba", "postgresql://user:secreto@localhost/db", "postgresql+asyncpg://", "postgresql+asyncpg://user:secreto@localhost:notaport/db"])
def test_direccion_invalida_no_expone_secreto(monkeypatch, value):
    from app.core.config import ConfigurationError
    if value is not None:
        monkeypatch.setenv("DATABASE_URL", value)
    with pytest.raises(ConfigurationError) as error:
        load_settings()
    assert str(error.value) == "DATABASE_URL debe indicar una base PostgreSQL con controlador asyncpg"
    assert error.value.__cause__ is None

@pytest.mark.parametrize("value,expected", [(None, False), ("false", False), ("TRUE", True)])
def test_sql_echo_interpreta_booleano(monkeypatch, value, expected):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:ejemplo@localhost/db")
    if value is not None:
        monkeypatch.setenv("SQL_ECHO", value)
    assert load_settings().sql_echo is expected


def test_sql_echo_invalido_es_error_propio(monkeypatch):
    from app.core.config import ConfigurationError
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:ejemplo@localhost/db")
    monkeypatch.setenv("SQL_ECHO", "talvez:secreto")
    with pytest.raises(ConfigurationError, match="SQL_ECHO debe ser true o false"):
        load_settings()
