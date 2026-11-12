"""El aviso de comprobante se agenda sólo tras una venta confirmada y no bloquea."""
import asyncio
import logging
import socket
import time
from decimal import Decimal

import pytest
from httpx import AsyncClient
import uvicorn


@pytest.mark.asyncio
async def test_post_venta_agenda_aviso_solo_si_confirma(client, sale_seed, monkeypatch):
    from app.modules.ventas import service

    calls = []

    async def spy(venta_id, total):
        calls.append((venta_id, total))

    monkeypatch.setattr(service, 'avisar_comprobante', spy)
    async with sale_seed() as seed:
        cliente = await seed.cliente('Agenda Aviso', 'agenda-c05@example.test')
        libro = await seed.libro('Libro agenda C05', '10.00')

        rejected = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': 999999999, 'cantidad': 1}],
        })
        assert rejected.status_code == 409
        assert calls == []

        created = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 2}],
        })
        assert created.status_code == 201
        assert calls == [(created.json()['id'], Decimal('20.00'))]


@pytest.mark.asyncio
async def test_aviso_no_bloquea_respuesta_ni_otras_peticiones(database_url, application, sale_seed, caplog):
    caplog.set_level(logging.INFO, logger='app.modules.ventas.service')
    async with sale_seed() as seed:
        cliente = await seed.cliente('Aviso Real', 'aviso-real-c05@example.test')
        libro = await seed.libro('Libro aviso real C05', '30.00')

        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(
            'app.main:app', host='127.0.0.1', port=port, loop='asyncio',
            http='h11', lifespan='on', log_level='warning',
        ))
        task = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            async with asyncio.timeout(10):
                while not server.started:
                    if task.done():
                        await task
                        pytest.fail('Uvicorn terminó antes de servir')
                    await asyncio.sleep(0.02)
            async with AsyncClient(base_url=f'http://127.0.0.1:{port}') as real:
                started = time.perf_counter()
                created = await real.post('/ventas/', json={
                    'cliente_id': cliente,
                    'renglones': [{'libro_id': libro, 'cantidad': 1}],
                })
                elapsed = time.perf_counter() - started
                assert created.status_code == 201
                venta_id = created.json()['id']
                assert elapsed < 0.5
                assert not any('Comprobante' in record.getMessage() for record in caplog.records)

                started = time.perf_counter()
                alive = await real.get('/health/live')
                assert alive.status_code == 200
                assert time.perf_counter() - started < 0.5

                async with asyncio.timeout(3):
                    while not any('Comprobante' in record.getMessage() for record in caplog.records):
                        await asyncio.sleep(0.05)
                assert any(
                    str(venta_id) in record.getMessage() and '30.00' in record.getMessage()
                    for record in caplog.records
                    if record.name == 'app.modules.ventas.service'
                )
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, timeout=10)
            listener.close()
