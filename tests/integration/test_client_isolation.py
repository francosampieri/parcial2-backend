"""Aislamiento de datos HTTP de clientes."""
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_fixture_conserva_cliente_ajeno(application, client_seed):
    async with application.state.engine.begin() as conn:
        await conn.execute(text("INSERT INTO cliente (nombre, email) VALUES ('Ajeno', 'ajeno-c04@example.test')"))
    try:
        async with client_seed() as seed:
            await seed('Propio', 'propio-c04@example.test')
        async with application.state.engine.connect() as conn:
            emails = (await conn.execute(text("SELECT email FROM cliente WHERE email IN ('ajeno-c04@example.test', 'propio-c04@example.test')"))).scalars().all()
        assert emails == ['ajeno-c04@example.test']
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM cliente WHERE email = 'ajeno-c04@example.test'"))


@pytest.mark.asyncio
async def test_fixture_aisla_bloques_consecutivos(application, client_seed):
    async with client_seed() as seed:
        await seed('Primero', 'primero-c04@example.test')
    async with client_seed() as seed:
        await seed('Segundo', 'segundo-c04@example.test')
        async with application.state.engine.connect() as conn:
            emails = (await conn.execute(text("SELECT email FROM cliente WHERE email IN ('primero-c04@example.test', 'segundo-c04@example.test')"))).scalars().all()
        assert emails == ['segundo-c04@example.test']
