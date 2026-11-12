"""Contratos HTTP de editoriales sobre PostgreSQL aislado."""
import pytest
from sqlalchemy import text
from sqlalchemy import event


@pytest.mark.asyncio
async def test_crear_editorial_devuelve_201(client, application):
    try:
        response = await client.post('/editoriales/', json={'nombre': 'Editorial C03', 'pais': 'AR'})
        assert response.status_code == 201
        assert response.json()['nombre'] == 'Editorial C03'
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM editorial WHERE nombre = 'Editorial C03'"))


@pytest.mark.asyncio
async def test_editorial_rechaza_duplicado_y_acepta_otro_nombre(client, application):
    try:
        assert (await client.post('/editoriales/', json={'nombre': 'Unica C03', 'pais': 'AR'})).status_code == 201
        conflict = await client.post('/editoriales/', json={'nombre': 'Unica C03', 'pais': 'UY'})
        assert conflict.status_code == 409
        assert 'INSERT' not in conflict.text
        assert (await client.post('/editoriales/', json={'nombre': 'Otra C03', 'pais': 'UY'})).status_code == 201
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM editorial WHERE nombre IN ('Unica C03', 'Otra C03')"))


@pytest.mark.asyncio
@pytest.mark.parametrize('extra', [{'id': 1}, {'desconocido': 'valor'}])
async def test_editorial_rechaza_campos_no_declarados(client, extra):
    data = {'nombre': 'Rechazada C03', 'pais': 'AR', **extra}
    assert (await client.post('/editoriales/', json=data)).status_code == 422


@pytest.mark.asyncio
async def test_editorial_detalle_lista_y_patch(client, catalog_seed):
    async with catalog_seed() as seed:
        await seed('Lista A C03')
        await seed('Lista B C03')
        listing = await client.get('/editoriales/', params={'limit': 1})
        assert listing.status_code == 200
        first_id = listing.json()[0]['id']
        page2 = await client.get('/editoriales/', params={'limit': 1, 'offset': 1})
        assert page2.json()[0]['id'] > first_id
        detail = await client.get(f'/editoriales/{first_id}')
        assert detail.status_code == 200
        patched = await client.patch(f'/editoriales/{first_id}', json={'pais': 'UY'})
        assert patched.status_code == 200
        assert patched.json()['nombre'] == detail.json()['nombre']
        assert patched.json()['pais'] == 'UY'
        assert (await client.patch(f'/editoriales/{first_id}', json={'nombre': None})).status_code == 422
        assert (await client.get('/editoriales/no-es-entero')).status_code == 422
        assert (await client.get('/editoriales/999999999')).status_code == 404
        assert (await client.get('/editoriales/', params={'limit': 0})).status_code == 422


@pytest.mark.asyncio
async def test_editorial_patch_conflicto_y_nulos(client, catalog_seed):
    async with catalog_seed() as seed:
        await seed('Patch A C03')
        await seed('Patch B C03')
        rows = (await client.get('/editoriales/')).json()
        first = next(row for row in rows if row['nombre'] == 'Patch A C03')
        response = await client.patch(f"/editoriales/{first['id']}", json={'nombre': 'Patch B C03'})
        assert response.status_code == 409
        assert (await client.get(f"/editoriales/{first['id']}")).json() == first
        assert (await client.patch(f"/editoriales/{first['id']}", json={'pais': None})).status_code == 422
        assert (await client.patch('/editoriales/999999999', json={'pais': 'AR'})).status_code == 404
        for params in ({'limit': 101}, {'offset': -1}):
            assert (await client.get('/editoriales/', params=params)).status_code == 422


@pytest.mark.asyncio
async def test_libros_de_editorial_vacia_y_paginados(client, application, catalog_seed):
    assert (await client.get('/editoriales/999999999/libros')).status_code == 404
    async with catalog_seed() as seed:
        await seed('Editorial libros C03')
        rows = (await client.get('/editoriales/')).json()
        id_ = next(row['id'] for row in rows if row['nombre'] == 'Editorial libros C03')
        assert (await client.get(f'/editoriales/{id_}/libros')).json() == []
        try:
            async with application.state.engine.begin() as conn:
                for n in (1, 2):
                    await conn.execute(text("INSERT INTO libro (isbn, titulo, precio, stock, editorial_id) VALUES (:isbn, :title, 10, 1, :id)"), {'isbn': f'editorial-c03-{n}', 'title': f'Título {n}', 'id': id_})
            response = await client.get(f'/editoriales/{id_}/libros', params={'limit': 1, 'offset': 1})
            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]['titulo'] == 'Título 2'
            assert response.json()[0]['editorial']['id'] == id_
            assert (await client.get(f'/editoriales/{id_}/libros', params={'limit': 0})).status_code == 422
            statements = []
            def observe(*args):
                statements.append(args[2])
            event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            try:
                all_books = await client.get(f'/editoriales/{id_}/libros')
                assert len(all_books.json()) == 2
                assert len(statements) == 2  # padre y listado con relaciones, sin SQL por fila
            finally:
                event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        finally:
            async with application.state.engine.begin() as conn:
                await conn.execute(text("DELETE FROM libro WHERE editorial_id = :id"), {'id': id_})
