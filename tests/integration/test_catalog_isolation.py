"""Comprobar aislamiento de los recursos HTTP de catálogo."""
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_catalogo_fixture_limpia_sus_filas_y_preserva_ajenas(application, catalog_seed):
    async with application.state.engine.begin() as conn:
        await conn.execute(text("INSERT INTO editorial (nombre, pais) VALUES ('ajena-c03', 'AR')"))
    try:
        async with catalog_seed() as seed:
            await seed("propia-c03")
        async with application.state.engine.connect() as conn:
            rows = (await conn.execute(text("SELECT nombre FROM editorial WHERE nombre IN ('ajena-c03', 'propia-c03')"))).scalars().all()
        assert rows == ["ajena-c03"]
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM editorial WHERE nombre = 'ajena-c03'"))


@pytest.mark.asyncio
async def test_catalogo_fixture_aisla_bloques_consecutivos(application, catalog_seed):
    async with catalog_seed() as seed:
        await seed("primera-c03")
    async with catalog_seed() as seed:
        await seed("segunda-c03")
        async with application.state.engine.connect() as conn:
            rows = (await conn.execute(text("SELECT nombre FROM editorial WHERE nombre IN ('primera-c03', 'segunda-c03')"))).scalars().all()
        assert rows == ["segunda-c03"]
