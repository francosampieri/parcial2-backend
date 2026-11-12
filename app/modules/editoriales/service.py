"""Operaciones asincrónicas sobre editoriales."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import EditorialCreate, EditorialUpdate
from app.modules.libros.models import Libro


async def crear(session: AsyncSession, data: EditorialCreate) -> Editorial:
    editorial = Editorial(**data.model_dump())
    session.add(editorial)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    await session.refresh(editorial)
    return editorial


async def obtener(session: AsyncSession, id_: int) -> Editorial:
    editorial = await session.get(Editorial, id_)
    if editorial is None:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")
    return editorial


async def listar(session: AsyncSession, limit: int, offset: int) -> list[Editorial]:
    return list((await session.scalars(select(Editorial).order_by(Editorial.id).limit(limit).offset(offset))).all())


async def actualizar(session: AsyncSession, id_: int, data: EditorialUpdate) -> Editorial:
    editorial = await obtener(session, id_)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(editorial, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    return editorial


async def libros(session: AsyncSession, id_: int, limit: int, offset: int) -> list[Libro]:
    await obtener(session, id_)
    stmt = (select(Libro).where(Libro.editorial_id == id_)
            .options(joinedload(Libro.editorial), joinedload(Libro.genero))
            .order_by(Libro.id).limit(limit).offset(offset))
    return list((await session.scalars(stmt)).all())
