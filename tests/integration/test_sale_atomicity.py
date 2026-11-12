"""Atomicidad y validación de referencias al registrar ventas."""
import pytest
from sqlalchemy import text


async def _contar(application, cliente_id):
    async with application.state.engine.connect() as conn:
        return (await conn.execute(
            text('SELECT count(*) FROM venta WHERE cliente_id = :id'), {'id': cliente_id}
        )).scalar_one()


@pytest.mark.asyncio
async def test_post_venta_cliente_inexistente_409_sin_filas(client, application, sale_seed):
    async with sale_seed() as seed:
        libro = await seed.libro('Libro cliente ausente C05', '100.00')
        response = await client.post('/ventas/', json={
            'cliente_id': 999999999,
            'renglones': [{'libro_id': libro, 'cantidad': 1}],
        })
        assert response.status_code == 409
        assert 'SELECT' not in response.text and 'foreign key' not in response.text.lower()
        assert await _contar(application, 999999999) == 0


@pytest.mark.asyncio
async def test_post_venta_libro_inexistente_409_sin_cabecera(client, application, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Venta libro ausente', 'libro-ausente-c05@example.test')
        libro = await seed.libro('Libro presente C05', '100.00')

        response = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 1}, {'libro_id': 999999999, 'cantidad': 1}],
        })

        assert response.status_code == 409
        assert await _contar(application, cliente) == 0
        async with application.state.engine.connect() as conn:
            renglones = (await conn.execute(
                text('SELECT count(*) FROM renglon_venta WHERE libro_id = :id'), {'id': libro}
            )).scalar_one()
        assert renglones == 0


@pytest.mark.asyncio
async def test_post_venta_fallida_permite_venta_valida_posterior(client, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Venta recuperada', 'recuperada-c05@example.test')
        libro = await seed.libro('Libro recuperado C05', '50.00')
        rejected = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 1}, {'libro_id': 999999999, 'cantidad': 1}],
        })
        assert rejected.status_code == 409
        ok = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 1}],
        })
        assert ok.status_code == 201
        assert ok.json()['total'] == '50.00'


@pytest.mark.asyncio
async def test_integridad_fk_al_confirmar_409_sin_filas_y_recuperacion(client, application, sale_seed, monkeypatch):
    from app.modules.ventas import service

    async with sale_seed() as seed:
        cliente = await seed.cliente('Integridad FK', 'integridad-c05@example.test')
        libro = await seed.libro('Libro borrado C05', '60.00')
        original = service._cargar_libros

        async def cargar_y_borrar(session, ids):
            libros = await original(session, ids)
            async with application.state.engine.begin() as conn:
                await conn.execute(text('DELETE FROM libro WHERE id = :id'), {'id': libro})
            return libros

        monkeypatch.setattr(service, '_cargar_libros', cargar_y_borrar)
        response = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 1}],
        })

        assert response.status_code == 409
        assert 'INSERT' not in response.text and 'violates' not in response.text.lower()
        assert await _contar(application, cliente) == 0

        monkeypatch.setattr(service, '_cargar_libros', original)
        posterior = await seed.libro('Libro posterior C05', '40.00')
        valid = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': posterior, 'cantidad': 1}],
        })
        assert valid.status_code == 201


@pytest.mark.asyncio
@pytest.mark.parametrize('renglones', [
    [],
    [{'libro_id': 1, 'cantidad': 1}, {'libro_id': 1, 'cantidad': 2}],
    [{'libro_id': 1, 'cantidad': 0}],
    [{'libro_id': 1, 'cantidad': -1}],
    [{'libro_id': 1, 'cantidad': 1, 'precio_unitario': '1.00'}],
    [{'libro_id': 1, 'cantidad': 1, 'desconocido': 1}],
])
async def test_post_venta_contrato_invalido_422_sin_filas(client, application, sale_seed, renglones):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Venta inválida', 'invalida-c05@example.test')
        libro = await seed.libro('Libro inválido C05', '10.00')
        normalized = [
            {**item, 'libro_id': libro} if item.get('libro_id') == 1 else item
            for item in renglones
        ]
        response = await client.post('/ventas/', json={'cliente_id': cliente, 'renglones': normalized})
        assert response.status_code == 422
        assert await _contar(application, cliente) == 0
