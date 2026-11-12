"""Lecturas de ventas: listado, detalle, ventas por cliente y consultas acotadas."""
import pytest
from sqlalchemy import event


async def _crear(client, cliente_id, renglones):
    response = await client.post('/ventas/', json={'cliente_id': cliente_id, 'renglones': renglones})
    assert response.status_code == 201
    return response.json()


async def _ids(application):
    from sqlalchemy import text
    async with application.state.engine.connect() as conn:
        return [row[0] for row in (await conn.execute(text('SELECT id FROM venta ORDER BY id'))).all()]


@pytest.mark.asyncio
async def test_listado_ventas_resumen_paginado_y_orden_estable(client, application, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Listado Ventas', 'listado-c05@example.test')
        libro = await seed.libro('Libro listado C05', '100.00')
        first = await _crear(client, cliente, [{'libro_id': libro, 'cantidad': 1}])
        second = await _crear(client, cliente, [{'libro_id': libro, 'cantidad': 2}])

        response = await client.get('/ventas/', params={'limit': 100, 'offset': 0})
        assert response.status_code == 200
        items = response.json()
        ids = [item['id'] for item in items]
        assert ids.index(first['id']) < ids.index(second['id'])
        summary = next(item for item in items if item['id'] == first['id'])
        assert set(summary) == {'id', 'fecha', 'total', 'cliente'}
        assert summary['cliente']['id'] == cliente
        assert summary['total'] == '100.00'

        one = await client.get('/ventas/', params={'limit': 1, 'offset': 0})
        assert len(one.json()) == 1
        empty = await client.get('/ventas/', params={'limit': 20, 'offset': 1_000_000})
        assert empty.json() == []


@pytest.mark.asyncio
@pytest.mark.parametrize('params', [
    {'limit': 0}, {'limit': 101}, {'offset': -1},
])
async def test_listado_ventas_paginacion_invalida_422(client, params):
    assert (await client.get('/ventas/', params=params)).status_code == 422


@pytest.mark.asyncio
async def test_detalle_venta_y_errores(client, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Detalle Venta', 'detalle-c05@example.test')
        uno = await seed.libro('Detalle Libro Uno C05', '11.11')
        dos = await seed.libro('Detalle Libro Dos C05', '22.22')
        sale = await _crear(client, cliente, [
            {'libro_id': uno, 'cantidad': 2},
            {'libro_id': dos, 'cantidad': 1},
        ])

        response = await client.get(f"/ventas/{sale['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == sale['id']
        assert [item['titulo'] for item in data['renglones']] == ['Detalle Libro Uno C05', 'Detalle Libro Dos C05']
        assert [item['subtotal'] for item in data['renglones']] == ['22.22', '22.22']
        assert data['total'] == '44.44'

        assert (await client.get('/ventas/999999999')).status_code == 404
        assert (await client.get('/ventas/no-entero')).status_code == 422


@pytest.mark.asyncio
async def test_ventas_por_cliente_filtra_pagina_y_valida(client, sale_seed):
    async with sale_seed() as seed:
        cliente_a = await seed.cliente('Cliente Ventas A', 'ventas-a-c05@example.test')
        cliente_b = await seed.cliente('Cliente Ventas B', 'ventas-b-c05@example.test')
        cliente_sin = await seed.cliente('Cliente Sin Ventas', 'sin-ventas-c05@example.test')
        libro = await seed.libro('Libro por cliente C05', '10.00')
        a_uno = await _crear(client, cliente_a, [{'libro_id': libro, 'cantidad': 1}])
        a_dos = await _crear(client, cliente_a, [{'libro_id': libro, 'cantidad': 2}])
        b_uno = await _crear(client, cliente_b, [{'libro_id': libro, 'cantidad': 3}])

        response = await client.get(f'/clientes/{cliente_a}/ventas', params={'limit': 100, 'offset': 0})
        assert response.status_code == 200
        ids = [item['id'] for item in response.json()]
        assert ids == [a_uno['id'], a_dos['id']]
        assert b_uno['id'] not in ids
        assert all(set(item) == {'id', 'fecha', 'total', 'cliente'} for item in response.json())
        assert (await client.get(f'/clientes/{cliente_b}/ventas')).json()[0]['id'] == b_uno['id']
        assert (await client.get(f'/clientes/{cliente_sin}/ventas')).json() == []
        assert (await client.get('/clientes/999999999/ventas')).status_code == 404
        assert (await client.get('/clientes/no-entero/ventas')).status_code == 422
        assert (await client.get(f'/clientes/{cliente_a}/ventas', params={'limit': 0})).status_code == 422


@pytest.mark.asyncio
async def test_consultas_acotadas_en_listado_detalle_y_cliente(client, application, sale_seed):
    async with sale_seed() as seed:
        cliente = await seed.cliente('Conteo SQL', 'conteo-c05@example.test')
        uno = await seed.libro('Conteo Libro Uno C05', '1.00')
        dos = await seed.libro('Conteo Libro Dos C05', '2.00')
        tres = await seed.libro('Conteo Libro Tres C05', '3.00')
        corta = await _crear(client, cliente, [{'libro_id': uno, 'cantidad': 1}])
        larga = await _crear(client, cliente, [
            {'libro_id': uno, 'cantidad': 1},
            {'libro_id': dos, 'cantidad': 1},
            {'libro_id': tres, 'cantidad': 1},
        ])

        counts = {}
        def observe(*args):
            counts['sql'] += 1

        async def medir(action):
            counts['sql'] = 0
            event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            try:
                response = await action()
            finally:
                event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            assert response.status_code == 200
            return counts['sql']

        corto = await medir(lambda: client.get(f"/ventas/{corta['id']}"))
        largo = await medir(lambda: client.get(f"/ventas/{larga['id']}"))
        listado = await medir(lambda: client.get('/ventas/', params={'limit': 100}))
        por_cliente = await medir(lambda: client.get(f'/clientes/{cliente}/ventas', params={'limit': 100}))

        assert corto == largo
        assert listado == 1
        assert por_cliente == 2
        assert corto <= 2
