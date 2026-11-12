"""Rutas HTTP de libros."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.libros import service
from app.modules.libros.schemas import LibroCreate, LibroDetail, LibroRead, LibroUpdate

router = APIRouter(prefix="/libros", tags=["libros"])


@router.post("/", response_model=LibroDetail, status_code=201)
async def crear(data: LibroCreate, session: AsyncSession = Depends(get_session)) -> LibroDetail:
    return await service.crear(session, data)


@router.get("/", response_model=list[LibroRead])
async def listar(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), titulo: str | None = None, genero_id: int | None = None, session: AsyncSession = Depends(get_session)) -> list[LibroRead]:
    return await service.listar(session, limit, offset, titulo, genero_id)


@router.get("/{id}", response_model=LibroDetail)
async def detalle(id: int, session: AsyncSession = Depends(get_session)) -> LibroDetail:
    return await service.detalle(session, id)


@router.patch("/{id}", response_model=LibroDetail)
async def actualizar(id: int, data: LibroUpdate, session: AsyncSession = Depends(get_session)) -> LibroDetail:
    return await service.actualizar(session, id, data)
