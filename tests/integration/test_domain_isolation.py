"""Aislamiento de las transacciones de prueba del dominio."""
import pytest
from sqlalchemy import text

@pytest.mark.asyncio
@pytest.mark.parametrize('valor', [11, 29])
async def test_sesion_privada_aísla_datos_y_revierte(domain_session, valor):
    await domain_session.execute(text('CREATE TEMP TABLE aislamiento_c02 (valor integer)'))
    assert (await domain_session.execute(text('SELECT count(*) FROM aislamiento_c02'))).scalar_one() == 0
    await domain_session.execute(text('INSERT INTO aislamiento_c02 VALUES (:valor)'), {'valor': valor})
    assert (await domain_session.execute(text('SELECT valor FROM aislamiento_c02'))).scalar_one() == valor

@pytest.mark.asyncio
async def test_rollback_no_borra_datos_ajenos(domain_session, application):
    from uuid import uuid4
    nombre = f'c02_aislamiento_{uuid4().hex}'
    async with application.state.engine.begin() as other:
        await other.execute(text(f'CREATE TABLE {nombre} (valor INTEGER)'))
        await other.execute(text(f'INSERT INTO {nombre} VALUES (17)'))
    try:
        await domain_session.execute(text(f'INSERT INTO {nombre} VALUES (23)'))
        await domain_session.rollback()
        async with application.state.engine.connect() as other:
            assert (await other.execute(text(f'SELECT valor FROM {nombre}'))).scalars().all() == [17]
    finally:
        async with application.state.engine.begin() as other:
            await other.execute(text(f'DROP TABLE {nombre}'))
