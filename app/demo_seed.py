"""Carga manual y conservadora de ejemplos para el parcial."""
import asyncio
import json
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import load_settings
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor
from app.modules import register_models


class SeedConflict(ValueError):
    """Un dato preexistente impediría reproducir el ejemplo sin alterarlo."""


async def _find_one(session: AsyncSession, model: type, **key: object):
    statement = select(model)
    for column, value in key.items():
        statement = statement.where(getattr(model, column) == value)
    matches = (await session.scalars(statement)).all()
    if len(matches) > 1:
        raise SeedConflict(f"Clave natural ambigua: {model.__name__} {key}")
    return matches[0] if matches else None


async def _ensure(session: AsyncSession, model: type, key: dict, values: dict):
    existing = await _find_one(session, model, **key)
    if existing is not None:
        for field, expected in values.items():
            if getattr(existing, field) != expected:
                raise SeedConflict(f"Dato existente diferente: {model.__name__} {key} ({field})")
        return existing
    record = model(**key, **values)
    session.add(record)
    await session.flush()
    return record


async def seed_examples(session: AsyncSession) -> dict[str, object]:
    """Insertar faltantes dentro de la transacción del llamador, sin commit propio."""
    editorial = await _ensure(session, Editorial, {"nombre": "Editorial totones"}, {"pais": "AR"})
    genero = await _ensure(session, Genero, {"nombre": "Narrativa totones"}, {})
    autores = []
    for nombre, nacionalidad in (("Julio Cortázar", "AR"), ("Ricardo Piglia", "AR")):
        autores.append(await _ensure(session, Autor, {"nombre": nombre, "nacionalidad": nacionalidad}, {}))
    libros = []
    examples = (
        ("9780000000001", "Rayuela", Decimal("25000.00"), autores[0]),
        ("9780000000002", "Libro de cuentos", Decimal("12000.00"), autores[0]),
        ("9780000000003", "Ensayos", Decimal("15000.00"), autores[1]),
        ("9780000000004", "Respiración artificial", Decimal("27000.00"), autores[1]),
    )
    for isbn, titulo, precio, autor in examples:
        libro = await _ensure(session, Libro, {"isbn": isbn}, {
            "titulo": titulo, "precio": precio, "stock": 10,
            "editorial_id": editorial.id, "genero_id": genero.id,
        })
        await _ensure(session, LibroAutor, {"libro_id": libro.id, "autor_id": autor.id},
                      {"rol": "autor", "orden": 1})
        libros.append(libro.id)
    await _ensure(session, LibroAutor, {"libro_id": libros[2], "autor_id": autores[0].id},
                  {"rol": "coautor", "orden": 2})
    cliente = await _ensure(session, Cliente, {"email": "cliente-demo@totones.example"},
                           {"nombre": "Cliente de ejemplo"})
    return {"editorial": editorial.id, "genero": genero.id,
            "autores": [autor.id for autor in autores], "libros": libros, "cliente": cliente.id}


async def main() -> None:
    register_models()
    settings = load_settings()
    engine = create_async_engine(settings.database_url, echo=settings.sql_echo)
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                async with session.begin():
                    identifiers = await seed_examples(session)
        except SeedConflict as error:
            raise SystemExit(f"Seed no aplicado: {error}") from None
        print(json.dumps(identifiers, ensure_ascii=False))
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
