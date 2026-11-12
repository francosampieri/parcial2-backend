"""Punto de entrada ASGI; importar este módulo no accede a PostgreSQL."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import load_settings
from app.core.database import (
    DATABASE_ERRORS,
    DatabaseUnavailableError,
    initialize_database,
    is_database_unavailable,
)
from app.modules.health.router import router as health_router
from app.modules.editoriales.router import router as editoriales_router
from app.modules.generos.router import router as generos_router
from app.modules.autores.router import router as autores_router
from app.modules.libros.router import router as libros_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Poseer los recursos desde startup hasta apagado, también ante fallos."""
    settings = load_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.sql_echo,
        pool_pre_ping=True,
        connect_args={"timeout": 5},
    )
    application.state.engine = engine
    try:
        application.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            await initialize_database(engine)
        except DATABASE_ERRORS as error:
            if not is_database_unavailable(error):
                raise
            raise DatabaseUnavailableError("Base de datos no disponible") from None
        yield
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    """Cada llamada construye una aplicación con su propio ciclo de vida."""
    application = FastAPI(title="Librería — totones", lifespan=lifespan)
    application.add_exception_handler(DatabaseUnavailableError, database_unavailable_response)
    application.include_router(health_router)
    application.include_router(editoriales_router)
    application.include_router(generos_router)
    application.include_router(autores_router)
    application.include_router(libros_router)
    return application


async def database_unavailable_response(request: Request, error: Exception) -> JSONResponse:
    """Traducir también fallos de adquisición anteriores al handler de ruta."""
    return JSONResponse(status_code=503, content={"detail": "Base de datos no disponible"})


app = create_app()
