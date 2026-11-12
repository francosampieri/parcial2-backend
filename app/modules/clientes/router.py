"""Rutas HTTP de clientes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.clientes import service
from app.modules.clientes.schemas import ClienteCreate, ClienteRead, ClienteUpdate, PerfilCreate, PerfilRead

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/", response_model=ClienteRead, status_code=201)
async def crear(data: ClienteCreate, session: AsyncSession = Depends(get_session)) -> ClienteRead:
    return await service.crear(session, data)


@router.get("/{id}", response_model=ClienteRead)
async def obtener(id: int, session: AsyncSession = Depends(get_session)) -> ClienteRead:
    return await service.obtener(session, id)


@router.patch("/{id}", response_model=ClienteRead)
async def actualizar(id: int, data: ClienteUpdate, session: AsyncSession = Depends(get_session)) -> ClienteRead:
    return await service.actualizar(session, id, data)


@router.post("/{id}/perfil", response_model=PerfilRead, status_code=201)
async def crear_perfil(id: int, data: PerfilCreate, session: AsyncSession = Depends(get_session)) -> PerfilRead:
    return await service.crear_perfil(session, id, data)
