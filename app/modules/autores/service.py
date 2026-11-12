"""Operaciones de autores."""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.modules.autores.models import Autor
from app.modules.autores.schemas import AutorCreate, AutorUpdate
from app.modules.libros.models import Libro, LibroAutor
from app.modules.autores.schemas import LibroDeAutor
from app.modules.libros.schemas import LibroRead


async def crear(session: AsyncSession, data: AutorCreate) -> Autor:
    autor = Autor(**data.model_dump())
    session.add(autor)
    await session.commit()
    await session.refresh(autor)
    return autor


async def obtener(session: AsyncSession, id_: int) -> Autor:
    autor = await session.get(Autor, id_)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor


async def actualizar(session: AsyncSession, id_: int, data: AutorUpdate) -> Autor:
    autor = await obtener(session, id_)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(autor, field, value)
    await session.commit()
    return autor


async def libros(session: AsyncSession, id_: int, limit: int, offset: int) -> list[LibroDeAutor]:
    await obtener(session, id_)
    stmt = (select(LibroAutor).where(LibroAutor.autor_id == id_)
            .join(Libro).options(joinedload(LibroAutor.libro).joinedload(Libro.editorial),
                                 joinedload(LibroAutor.libro).joinedload(Libro.genero))
            .order_by(Libro.id).limit(limit).offset(offset))
    results = (await session.scalars(stmt)).all()
    return [LibroDeAutor(**LibroRead.model_validate(autoria.libro).model_dump(), rol=autoria.rol, orden=autoria.orden) for autoria in results]
