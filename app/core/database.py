"""Recursos SQLAlchemy asincrónicos; cada aplicación posee su motor."""
from collections.abc import AsyncIterator

import asyncpg
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.exc import (
    DBAPIError,
    DataError,
    DisconnectionError,
    IntegrityError,
    InterfaceError,
    OperationalError,
    ProgrammingError,
)
from sqlmodel import SQLModel

from app.modules import register_models


class DatabaseUnavailableError(RuntimeError):
    """Diagnóstico público de conexión, sin detalles del controlador."""


_CONNECTION_ERRORS = (
    OSError, TimeoutError, OperationalError, InterfaceError, DisconnectionError,
    asyncpg.PostgresConnectionError, asyncpg.InvalidAuthorizationSpecificationError,
    asyncpg.CannotConnectNowError, asyncpg.TooManyConnectionsError,
    asyncpg.InvalidCatalogNameError,
)
DATABASE_ERRORS = (*_CONNECTION_ERRORS, DBAPIError)


def is_database_unavailable(error: BaseException) -> bool:
    """Distinguir desconexiones de errores SQL/datos que requieren corregir código."""
    if isinstance(error, (ProgrammingError, IntegrityError, DataError)):
        return False
    return isinstance(error, _CONNECTION_ERRORS) or (
        isinstance(error, DBAPIError) and error.connection_invalidated
    )


async def initialize_database(engine: AsyncEngine) -> None:
    """Conectar y crear sólo tablas faltantes, sin migrar ni borrar datos."""
    register_models()
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Cerrar la sesión al terminar; cada service decide sus commits."""
    try:
        async with request.app.state.session_factory() as session:
            yield session
    except DATABASE_ERRORS as error:
        if not is_database_unavailable(error):
            raise
        raise DatabaseUnavailableError("Base de datos no disponible") from None
