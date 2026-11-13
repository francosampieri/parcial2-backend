"""Aviso de comprobante posterior a la respuesta."""
import asyncio
import logging
from decimal import Decimal

import pytest


@pytest.mark.asyncio
async def test_aviso_comprobante_espera_y_registra(caplog):
    from app.modules.ventas.service import avisar_comprobante

    caplog.set_level(logging.INFO, logger='app.modules.ventas.service')
    started = asyncio.get_running_loop().time()
    await avisar_comprobante(7, Decimal('123.45'))
    elapsed = asyncio.get_running_loop().time() - started

    assert elapsed >= 0.5
    assert any(
        '7' in record.getMessage() and '123.45' in record.getMessage()
        for record in caplog.records
        if record.name == 'app.modules.ventas.service'
    )


@pytest.mark.parametrize(('venta_id', 'total'), [(8, '77.00'), (9, '123.45')])
@pytest.mark.asyncio
async def test_aviso_visible_en_logger_de_uvicorn(monkeypatch, venta_id, total):
    from app.modules.ventas.service import avisar_comprobante

    mensajes = []
    monkeypatch.setattr(logging.getLogger('uvicorn.error'), 'info',
                        lambda mensaje, *args: mensajes.append(mensaje % args))

    await avisar_comprobante(venta_id, Decimal(total))

    assert mensajes == [f'Comprobante emitido para venta {venta_id} por {total}']
