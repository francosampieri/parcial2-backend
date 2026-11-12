"""Rutas HTTP de autores."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.autores import service
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate, LibroDeAutor

router = APIRouter(prefix="/autores", tags=["autores"])


@router.post("/", response_model=AutorRead, status_code=201)
async def crear(data: AutorCreate, session: AsyncSession = Depends(get_session)) -> AutorRead:
    return await service.crear(session, data)


@router.get("/{id}", response_model=AutorRead)
async def obtener(id: int, session: AsyncSession = Depends(get_session)) -> AutorRead:
    return await service.obtener(session, id)


@router.patch("/{id}", response_model=AutorRead)
async def actualizar(id: int, data: AutorUpdate, session: AsyncSession = Depends(get_session)) -> AutorRead:
    return await service.actualizar(session, id, data)


@router.get("/{id}/libros", response_model=list[LibroDeAutor])
async def libros(id: int, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), session: AsyncSession = Depends(get_session)) -> list[LibroDeAutor]:
    return await service.libros(session, id, limit, offset)
