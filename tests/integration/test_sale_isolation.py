"""Aislamiento de las fixtures de ventas en PostgreSQL privado."""
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_sale_seed_crea_ids_independientes_y_limpia_solo_lo_propio(application, sale_seed):
    async with sale_seed() as first:
        cliente_uno = await first.cliente('Iso Venta Uno', 'iso-venta-uno-c05@example.test')
        libro_uno = await first.libro('Iso Libro Uno', '10.00')
    async with sale_seed() as second:
        cliente_dos = await second.cliente('Iso Venta Dos', 'iso-venta-dos-c05@example.test')
        libro_dos = await second.libro('Iso Libro Dos', '20.00')
        assert cliente_uno != cliente_dos
        assert libro_uno != libro_dos
        async with application.state.engine.connect() as conn:
            clientes = (await conn.execute(text('SELECT count(*) FROM cliente WHERE id = ANY(:ids)'), {'ids': [cliente_uno]})).scalar_one()
            libros = (await conn.execute(text('SELECT count(*) FROM libro WHERE id = ANY(:ids)'), {'ids': [libro_uno]})).scalar_one()
        assert clientes == 0
        assert libros == 0


@pytest.mark.asyncio
async def test_sale_seed_preserva_filas_ajenas(application, sale_seed):
    async with application.state.engine.begin() as conn:
        ajeno = (await conn.execute(text(
            "INSERT INTO cliente (nombre, email) VALUES ('Ajeno C05', 'ajeno-c05@example.test') RETURNING id"
        ))).scalar_one()
    try:
        async with sale_seed() as seed:
            await seed.cliente('Propio C05', 'propio-c05@example.test')
            await seed.libro('Propio Libro C05', '15.00')
        async with application.state.engine.connect() as conn:
            conservado = (await conn.execute(text('SELECT count(*) FROM cliente WHERE id = :id'), {'id': ajeno})).scalar_one()
        assert conservado == 1
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text('DELETE FROM cliente WHERE id = :id'), {'id': ajeno})
