"""Consultas de salud del proceso y su dependencia PostgreSQL."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.health.schemas import LiveResponse, ReadyResponse
from app.modules.health.service import check_database

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=LiveResponse)
async def live() -> LiveResponse:
    """Responder sin abrir sesión ni consultar la base."""
    return LiveResponse()


@router.get("/ready", response_model=ReadyResponse)
async def ready(session: Annotated[AsyncSession, Depends(get_session)]) -> ReadyResponse:
    """Consultar PostgreSQL nuevamente en esta petición."""
    await check_database(session)
    return ReadyResponse()
