"""Configuración local leída al iniciar, sin efectos de red al importar."""
from dataclasses import dataclass, field
import os

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class ConfigurationError(ValueError):
    """Diagnóstico propio sin incluir valores privados."""


@dataclass(frozen=True)
class Settings:
    database_url: str = field(repr=False)
    sql_echo: bool = False


def load_settings() -> Settings:
    """El entorno conserva prioridad sobre el archivo local."""
    load_dotenv(dotenv_path=".env", override=False)
    address = os.environ.get("DATABASE_URL", "")
    try:
        parsed = make_url(address)
        valid = parsed.drivername == "postgresql+asyncpg" and bool(parsed.host and parsed.database)
    except (ArgumentError, ValueError):
        valid = False
    if not valid:
        raise ConfigurationError("DATABASE_URL debe indicar una base PostgreSQL con controlador asyncpg") from None
    echo = os.environ.get("SQL_ECHO", "false").lower()
    if echo not in {"true", "false"}:
        raise ConfigurationError("SQL_ECHO debe ser true o false")
    return Settings(database_url=address, sql_echo=echo == "true")

