"""Operaciones de géneros."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate
from app.modules.libros.models import Libro


async def crear(session: AsyncSession, data: GeneroCreate) -> Genero:
    genero = Genero(**data.model_dump())
    session.add(genero)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    await session.refresh(genero)
    return genero


async def listar(session: AsyncSession, limit: int, offset: int) -> list[Genero]:
    return list((await session.scalars(select(Genero).order_by(Genero.id).limit(limit).offset(offset))).all())


async def libros(session: AsyncSession, id_: int, limit: int, offset: int) -> list[Libro]:
    if await session.get(Genero, id_) is None:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    stmt = (select(Libro).where(Libro.genero_id == id_)
            .options(joinedload(Libro.editorial), joinedload(Libro.genero))
            .order_by(Libro.id).limit(limit).offset(offset))
    return list((await session.scalars(stmt)).all())
