"""Contratos HTTP de ventas y comprobantes en PostgreSQL privado."""
from datetime import datetime

import pytest


def test_openapi_ventas_publica_cuatro_rutas_async():
    import inspect

    from app.main import create_app

    application = create_app()
    schema = application.openapi()
    operations = {
        (path, method)
        for path, item in schema['paths'].items()
        if path.startswith('/ventas') or path == '/clientes/{id}/ventas'
        for method in item
        if method in {'get', 'post', 'patch', 'put', 'delete'}
    }
    assert operations == {
        ('/ventas/', 'post'),
        ('/ventas/', 'get'),
        ('/ventas/{id}', 'get'),
        ('/clientes/{id}/ventas', 'get'),
    }
    assert all(
        inspect.iscoroutinefunction(route.endpoint)
        for route in application.routes
        if getattr(route, 'path', '').startswith('/ventas')
        or getattr(route, 'path', '') == '/clientes/{id}/ventas'
    )


@pytest.mark.asyncio
async def test_post_venta_crea_con_dos_renglones_y_precios_copiados(client, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Tomás Ríos', 'tomas-venta-c05@example.test')
        primero = await seed.libro('Rayuela', '25000.00')
        segundo = await seed.libro('Respiración artificial', '27000.00')

        response = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': primero, 'cantidad': 2}, {'libro_id': segundo, 'cantidad': 1}],
        })

        assert response.status_code == 201
        data = response.json()
        assert data['id'] > 0
        assert data['cliente'] == {'id': cliente, 'nombre': 'Tomás Ríos', 'email': 'tomas-venta-c05@example.test'}
        assert [item['libro_id'] for item in data['renglones']] == [primero, segundo]
        assert [item['titulo'] for item in data['renglones']] == ['Rayuela', 'Respiración artificial']
        assert [item['cantidad'] for item in data['renglones']] == [2, 1]
        assert [item['precio_unitario'] for item in data['renglones']] == ['25000.00', '27000.00']
        assert [item['subtotal'] for item in data['renglones']] == ['50000.00', '27000.00']
        assert data['total'] == '77000.00'
        assert 'venta' not in data['renglones'][0]
        fecha = datetime.fromisoformat(data['fecha'].replace('Z', '+00:00'))
        assert fecha.utcoffset() is not None


@pytest.mark.asyncio
async def test_venta_conserva_precio_historico_tras_patch_libro(client, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Precio histórico', 'historico-c05@example.test')
        libro = await seed.libro('Libro histórico C05', '25000.00')

        sale = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 2}],
        })
        assert sale.status_code == 201
        assert sale.json()['total'] == '50000.00'

        changed = await client.patch(f'/libros/{libro}', json={'precio': '30000.00'})
        assert changed.status_code == 200

        detail = await client.get(f'/ventas/{sale.json()["id"]}')
        assert detail.status_code == 200
        assert detail.json()['renglones'][0]['precio_unitario'] == '25000.00'
        assert detail.json()['renglones'][0]['subtotal'] == '50000.00'
        assert detail.json()['total'] == '50000.00'

@pytest.mark.asyncio
async def test_post_venta_un_renglon_con_importe_minimo(client, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Importe Mínimo', 'minimo-venta-c05@example.test')
        libro = await seed.libro('Libro de diez centavos', '0.10')

        response = await client.post('/ventas/', json={
            'cliente_id': cliente,
            'renglones': [{'libro_id': libro, 'cantidad': 3}],
        })

        assert response.status_code == 201
        data = response.json()
        assert data['total'] == '0.30'
        assert data['renglones'] == [{
            'libro_id': libro,
            'titulo': 'Libro de diez centavos',
            'cantidad': 3,
            'precio_unitario': '0.10',
            'subtotal': '0.30',
        }]
