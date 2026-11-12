"""El seed crea sólo datos faltantes y conserva datos ajenos."""
import pytest
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_seed_creates_examples_and_is_idempotent(domain_session):
    from app.demo_seed import seed_examples
    from app.modules.libros.models import Libro

    first = await seed_examples(domain_session)
    count = await domain_session.scalar(select(func.count()).select_from(Libro))
    second = await seed_examples(domain_session)
    assert await domain_session.scalar(select(func.count()).select_from(Libro)) == count
    assert first == second
    assert len(first["libros"]) >= 4
    assert first["cliente"] > 0


@pytest.mark.asyncio
async def test_seed_includes_book_with_multiple_authors(domain_session):
    from app.demo_seed import seed_examples
    from app.modules.libros.models import LibroAutor

    ids = await seed_examples(domain_session)
    authors = (await domain_session.scalars(select(LibroAutor).where(LibroAutor.libro_id == ids["libros"][2]))).all()
    assert len(authors) == 2


@pytest.mark.asyncio
async def test_seed_rejects_conflicting_existing_data_without_overwriting(domain_session):
    from app.demo_seed import SeedConflict, seed_examples
    from app.modules.editoriales.models import Editorial

    domain_session.add(Editorial(nombre="Editorial totones", pais="UY"))
    await domain_session.flush()
    with pytest.raises(SeedConflict, match="Editorial totones"):
        await seed_examples(domain_session)
    editorial = await domain_session.scalar(select(Editorial).where(Editorial.nombre == "Editorial totones"))
    assert editorial.pais == "UY"


@pytest.mark.asyncio
async def test_seed_ambiguous_author_rolls_back_all_new_rows(domain_session):
    from app.demo_seed import SeedConflict, seed_examples
    from app.modules.autores.models import Autor
    from app.modules.editoriales.models import Editorial

    domain_session.add_all([
        Autor(nombre="Julio Cortázar", nacionalidad="AR"),
        Autor(nombre="Julio Cortázar", nacionalidad="AR"),
    ])
    await domain_session.flush()
    with pytest.raises(SeedConflict, match="ambigua"):
        async with domain_session.begin_nested():
            await seed_examples(domain_session)
    assert await domain_session.scalar(select(func.count()).select_from(Editorial).where(Editorial.nombre == "Editorial totones")) == 0
