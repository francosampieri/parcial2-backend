"""Operaciones asincrónicas de ventas y comprobantes."""
import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.clientes.models import Cliente
from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import (
    ClienteEnVenta,
    RenglonRead,
    VentaCreate,
    VentaDetail,
)

logger = logging.getLogger(__name__)


async def avisar_comprobante(venta_id: int, total: Decimal) -> None:
    """Simular el comprobante fuera de la respuesta y sin usar la sesión."""
    await asyncio.sleep(0.5)
    logger.info("Comprobante emitido para venta %s por %s", venta_id, total)
    logging.getLogger("uvicorn.error").info("Comprobante emitido para venta %s por %s", venta_id, total)


async def _cargar_libros(session: AsyncSession, ids: list[int]) -> dict[int, Libro]:
    return {
        libro.id: libro
        for libro in (await session.scalars(select(Libro).where(Libro.id.in_(ids)))).all()
    }


async def crear(session: AsyncSession, data: VentaCreate) -> VentaDetail:
    cliente = (await session.scalars(select(Cliente).where(Cliente.id == data.cliente_id))).first()
    if cliente is None:
        raise HTTPException(status_code=409, detail="Cliente o libro inexistente")

    libros = await _cargar_libros(session, [item.libro_id for item in data.renglones])
    if len(libros) != len({item.libro_id for item in data.renglones}):
        raise HTTPException(status_code=409, detail="Cliente o libro inexistente")

    total = sum(
        (libros[item.libro_id].precio * item.cantidad for item in data.renglones),
        Decimal("0.00"),
    ).quantize(Decimal("0.01"))
    venta = Venta(cliente_id=cliente.id, fecha=datetime.now(timezone.utc), total=total)
    session.add(venta)
    try:
        await session.flush()
        for item in data.renglones:
            session.add(RenglonVenta(
                venta_id=venta.id,
                libro_id=item.libro_id,
                cantidad=item.cantidad,
                precio_unitario=libros[item.libro_id].precio,
            ))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    return await detalle(session, venta.id)


async def listar(session: AsyncSession, limit: int, offset: int) -> list[Venta]:
    stmt = (
        select(Venta)
        .options(joinedload(Venta.cliente))
        .order_by(Venta.id)
        .limit(limit)
        .offset(offset)
    )
    return list((await session.scalars(stmt)).all())


async def por_cliente(session: AsyncSession, cliente_id: int, limit: int, offset: int) -> list[Venta]:
    existe = (await session.scalars(select(Cliente.id).where(Cliente.id == cliente_id))).first()
    if existe is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    stmt = (
        select(Venta)
        .where(Venta.cliente_id == cliente_id)
        .options(joinedload(Venta.cliente))
        .order_by(Venta.id)
        .limit(limit)
        .offset(offset)
    )
    return list((await session.scalars(stmt)).all())


async def detalle(session: AsyncSession, id_: int) -> VentaDetail:
    stmt = (
        select(Venta)
        .where(Venta.id == id_)
        .options(
            joinedload(Venta.cliente),
            selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
        )
    )
    venta = (await session.scalars(stmt)).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    renglones = sorted(venta.renglones, key=lambda item: item.id)
    return VentaDetail(
        id=venta.id,
        fecha=venta.fecha,
        total=venta.total,
        cliente=ClienteEnVenta.model_validate(venta.cliente),
        renglones=[
            RenglonRead(
                libro_id=item.libro_id,
                titulo=item.libro.titulo,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                subtotal=(item.precio_unitario * item.cantidad).quantize(Decimal("0.01")),
            )
            for item in renglones
        ],
    )
