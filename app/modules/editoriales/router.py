"""Rutas HTTP para editoriales."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.editoriales import service
from app.modules.editoriales.schemas import EditorialCreate, EditorialRead, EditorialUpdate
from app.modules.libros.schemas import LibroRead

router = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router.post("/", response_model=EditorialRead, status_code=201)
async def crear(data: EditorialCreate, session: AsyncSession = Depends(get_session)) -> EditorialRead:
    return await service.crear(session, data)


@router.get("/", response_model=list[EditorialRead])
async def listar(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), session: AsyncSession = Depends(get_session)) -> list[EditorialRead]:
    return await service.listar(session, limit, offset)


@router.get("/{id}", response_model=EditorialRead)
async def obtener(id: int, session: AsyncSession = Depends(get_session)) -> EditorialRead:
    return await service.obtener(session, id)


@router.patch("/{id}", response_model=EditorialRead)
async def actualizar(id: int, data: EditorialUpdate, session: AsyncSession = Depends(get_session)) -> EditorialRead:
    return await service.actualizar(session, id, data)


@router.get("/{id}/libros", response_model=list[LibroRead])
async def libros(id: int, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), session: AsyncSession = Depends(get_session)) -> list[LibroRead]:
    return await service.libros(session, id, limit, offset)
