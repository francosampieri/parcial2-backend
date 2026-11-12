"""Operaciones asincrónicas de clientes."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import ClienteCreate, ClienteUpdate, PerfilCreate


async def crear(session: AsyncSession, data: ClienteCreate) -> Cliente:
    cliente = Cliente(**data.model_dump())
    session.add(cliente)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    return await obtener(session, cliente.id)


async def obtener(session: AsyncSession, id_: int) -> Cliente:
    result = await session.scalars(
        select(Cliente).where(Cliente.id == id_).options(joinedload(Cliente.perfil))
    )
    cliente = result.one_or_none()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


async def actualizar(session: AsyncSession, id_: int, data: ClienteUpdate) -> Cliente:
    cliente = await obtener(session, id_)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    return cliente


async def crear_perfil(session: AsyncSession, id_: int, data: PerfilCreate) -> PerfilCliente:
    await obtener(session, id_)
    perfil = PerfilCliente(cliente_id=id_, **data.model_dump())
    session.add(perfil)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    await session.refresh(perfil)
    return perfil
