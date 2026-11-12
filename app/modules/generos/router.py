"""Rutas HTTP de géneros."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.generos import service
from app.modules.generos.schemas import GeneroCreate, GeneroRead
from app.modules.libros.schemas import LibroRead

router = APIRouter(prefix="/generos", tags=["generos"])


@router.post("/", response_model=GeneroRead, status_code=201)
async def crear(data: GeneroCreate, session: AsyncSession = Depends(get_session)) -> GeneroRead:
    return await service.crear(session, data)


@router.get("/", response_model=list[GeneroRead])
async def listar(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), session: AsyncSession = Depends(get_session)) -> list[GeneroRead]:
    return await service.listar(session, limit, offset)


@router.get("/{id}/libros", response_model=list[LibroRead])
async def libros(id: int, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), session: AsyncSession = Depends(get_session)) -> list[LibroRead]:
    return await service.libros(session, id, limit, offset)
