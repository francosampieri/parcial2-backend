"""Rutas HTTP de ventas y de ventas por cliente."""
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, VentaDetail, VentaRead


router = APIRouter(prefix="/ventas", tags=["ventas"])
clientes_router = APIRouter(prefix="/clientes", tags=["ventas"])


@router.post("/", response_model=VentaDetail, status_code=201)
async def crear(
    data: VentaCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> VentaDetail:
    venta = await service.crear(session, data)
    background_tasks.add_task(service.avisar_comprobante, venta.id, venta.total)
    return venta


@router.get("/", response_model=list[VentaRead])
async def listar(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[VentaRead]:
    return await service.listar(session, limit, offset)


@router.get("/{id}", response_model=VentaDetail)
async def detalle(id: int, session: AsyncSession = Depends(get_session)) -> VentaDetail:
    return await service.detalle(session, id)


@clientes_router.get("/{id}/ventas", response_model=list[VentaRead])
async def ventas_por_cliente(
    id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[VentaRead]:
    return await service.por_cliente(session, id, limit, offset)
