"""Contratos HTTP de autores."""
import pytest
from sqlalchemy import text
from sqlalchemy import event


@pytest.mark.asyncio
async def test_autor_crear_leer_y_modificar(client, application):
    try:
        response = await client.post('/autores/', json={'nombre': 'Autor C03', 'nacionalidad': 'AR'})
        assert response.status_code == 201
        id_ = response.json()['id']
        assert (await client.get(f'/autores/{id_}')).json()['nombre'] == 'Autor C03'
        changed = await client.patch(f'/autores/{id_}', json={'nacionalidad': 'UY'})
        assert changed.status_code == 200 and changed.json()['nombre'] == 'Autor C03'
        assert changed.json()['nacionalidad'] == 'UY'
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM autor WHERE nombre='Autor C03'"))


@pytest.mark.asyncio
async def test_autor_duplicado_permitido_nulos_y_referencias(client, application):
    try:
        first = await client.post('/autores/', json={'nombre': 'Repetido C03', 'nacionalidad': 'AR'})
        second = await client.post('/autores/', json={'nombre': 'Repetido C03', 'nacionalidad': 'UY'})
        assert first.status_code == second.status_code == 201
        assert first.json()['id'] != second.json()['id']
        id_ = first.json()['id']
        assert (await client.patch(f'/autores/{id_}', json={'nombre': None})).status_code == 422
        assert (await client.patch(f'/autores/{id_}', json={'nacionalidad': None})).status_code == 422
        assert (await client.patch(f'/autores/{id_}', json={'otro': 1})).status_code == 422
        assert (await client.post('/autores/', json={'nombre': 'Rechazo C03', 'nacionalidad': 'AR', 'id': 3})).status_code == 422
        assert (await client.get('/autores/abc')).status_code == 422
        assert (await client.get('/autores/999999999')).status_code == 404
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM autor WHERE nombre='Repetido C03'"))


@pytest.mark.asyncio
async def test_libros_por_autor_con_rol_y_orden(client, application):
    autor_id = None
    try:
        async with application.state.engine.begin() as conn:
            autor_id = (await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES ('Relacion C03','AR') RETURNING id"))).scalar_one()
            editorial_id = (await conn.execute(text("INSERT INTO editorial(nombre,pais) VALUES ('Relacion Editorial C03','AR') RETURNING id"))).scalar_one()
        assert (await client.get('/autores/999999999/libros')).status_code == 404
        empty = await client.get(f'/autores/{autor_id}/libros')
        assert empty.status_code == 200 and empty.json() == []
        async with application.state.engine.begin() as conn:
            second_autor = (await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES ('Relacion segundo C03','UY') RETURNING id"))).scalar_one()
            for n, rol in [(1, 'autor'), (2, 'traductor')]:
                libro_id = (await conn.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id) VALUES (:isbn,:titulo,10,1,:editorial) RETURNING id"), {'isbn': f'autor-c03-{n}', 'titulo': f'Libro Autor {n}', 'editorial': editorial_id})).scalar_one()
                await conn.execute(text("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES (:libro,:autor,:rol,1)"), {'libro': libro_id, 'autor': autor_id, 'rol': rol})
                if n == 2:
                    await conn.execute(text("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES (:libro,:autor,'coautor',1)"), {'libro': libro_id, 'autor': second_autor})
        response = await client.get(f'/autores/{autor_id}/libros', params={'limit': 1, 'offset': 1})
        assert response.status_code == 200
        assert response.json()[0]['titulo'] == 'Libro Autor 2'
        assert response.json()[0]['rol'] == 'traductor' and response.json()[0]['orden'] == 1
        second_response = await client.get(f'/autores/{second_autor}/libros')
        assert second_response.json()[0]['rol'] == 'coautor'
        assert second_response.json()[0]['orden'] == 1
        assert (await client.get(f'/autores/{autor_id}/libros', params={'limit': 0})).status_code == 422
        statements = []
        def observe(*args):
            statements.append(args[2])
        event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        try:
            all_books = await client.get(f'/autores/{autor_id}/libros')
            assert [book['rol'] for book in all_books.json()] == ['autor', 'traductor']
            assert len(statements) == 2
        finally:
            event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
    finally:
        async with application.state.engine.begin() as conn:
            if autor_id:
                await conn.execute(text("DELETE FROM libro_autor WHERE libro_id IN (SELECT id FROM libro WHERE isbn IN ('autor-c03-1','autor-c03-2'))"))
            await conn.execute(text("DELETE FROM libro WHERE isbn IN ('autor-c03-1','autor-c03-2')"))
            await conn.execute(text("DELETE FROM editorial WHERE nombre='Relacion Editorial C03'"))
            await conn.execute(text("DELETE FROM autor WHERE nombre IN ('Relacion C03','Relacion segundo C03')"))
