"""Operaciones asincrónicas sobre libros."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroDetail, LibroRead, LibroUpdate


async def crear(session: AsyncSession, data: LibroCreate) -> LibroDetail:
    book = Libro(**data.model_dump(exclude={"autores"}))
    session.add(book)
    try:
        await session.flush()
        for author in data.autores:
            session.add(LibroAutor(libro_id=book.id, **author.model_dump()))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    stmt = (select(Libro).where(Libro.id == book.id)
            .options(joinedload(Libro.editorial), joinedload(Libro.genero),
                     selectinload(Libro.autorias).joinedload(LibroAutor.autor))
            .execution_options(populate_existing=True))
    book = (await session.scalars(stmt)).one()
    return LibroDetail(**LibroRead.model_validate(book).model_dump(), autores=sorted(book.autorias, key=lambda a: (a.orden, a.autor_id)))


async def listar(session: AsyncSession, limit: int, offset: int, titulo: str | None, genero_id: int | None) -> list[Libro]:
    stmt = select(Libro).options(joinedload(Libro.editorial), joinedload(Libro.genero))
    if titulo is not None:
        stmt = stmt.where(Libro.titulo.icontains(titulo, autoescape=True))
    if genero_id is not None:
        stmt = stmt.where(Libro.genero_id == genero_id)
    stmt = stmt.order_by(Libro.id).limit(limit).offset(offset)
    return list((await session.scalars(stmt)).all())


async def detalle(session: AsyncSession, id_: int) -> LibroDetail:
    stmt = (select(Libro).where(Libro.id == id_)
            .options(joinedload(Libro.editorial), joinedload(Libro.genero),
                     selectinload(Libro.autorias).joinedload(LibroAutor.autor)))
    book = (await session.scalars(stmt)).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return LibroDetail(**LibroRead.model_validate(book).model_dump(), autores=sorted(book.autorias, key=lambda a: (a.orden, a.autor_id)))


async def actualizar(session: AsyncSession, id_: int, data: LibroUpdate) -> LibroDetail:
    book = await session.get(Libro, id_)
    if book is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos") from None
    return await detalle(session, id_)
