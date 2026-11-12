"""Comprobación de PostgreSQL con sesión explícita por petición."""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import DATABASE_ERRORS, DatabaseUnavailableError, is_database_unavailable


async def check_database(session: AsyncSession) -> None:
    """Ejecutar una consulta real, sin conservar disponibilidad en caché."""
    try:
        await session.execute(text("SELECT 1"))
    except DATABASE_ERRORS as error:
        if not is_database_unavailable(error):
            raise
        raise DatabaseUnavailableError("Base de datos no disponible") from None
