"""Contratos HTTP de géneros."""
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_genero_alta_y_lista(client, application):
    try:
        created = await client.post('/generos/', json={'nombre': 'Genero C03'})
        assert created.status_code == 201
        assert any(row['id'] == created.json()['id'] for row in (await client.get('/generos/')).json())
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM genero WHERE nombre = 'Genero C03'"))


@pytest.mark.asyncio
async def test_genero_conflicto_validacion_y_libros(client, application):
    try:
        first = await client.post('/generos/', json={'nombre': 'Genero relaciones C03'})
        id_ = first.json()['id']
        assert (await client.post('/generos/', json={'nombre': 'Genero relaciones C03'})).status_code == 409
        assert (await client.post('/generos/', json={'nombre': 'Otro C03', 'id': 5})).status_code == 422
        assert (await client.get('/generos/', params={'limit': 0})).status_code == 422
        assert (await client.get('/generos/999999999/libros')).status_code == 404
        empty = await client.get(f'/generos/{id_}/libros')
        assert empty.status_code == 200 and empty.json() == []
        async with application.state.engine.begin() as conn:
            editorial = (await conn.execute(text("INSERT INTO editorial (nombre,pais) VALUES ('Genero editor C03','AR') RETURNING id"))).scalar_one()
            await conn.execute(text("INSERT INTO libro (isbn,titulo,precio,stock,editorial_id,genero_id) VALUES ('genero-isbn-c03','Genero libro',10,1,:editorial,:genero)"), {'editorial': editorial, 'genero': id_})
        books = await client.get(f'/generos/{id_}/libros')
        assert books.status_code == 200 and books.json()[0]['titulo'] == 'Genero libro'
        assert books.json()[0]['genero']['id'] == id_
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM libro WHERE isbn='genero-isbn-c03'"))
            await conn.execute(text("DELETE FROM editorial WHERE nombre='Genero editor C03'"))
            await conn.execute(text("DELETE FROM genero WHERE nombre = 'Genero relaciones C03'"))


@pytest.mark.asyncio
async def test_generos_paginas_estables_y_validacion(client, application):
    try:
        first = await client.post('/generos/', json={'nombre': 'Pagina A C03'})
        second = await client.post('/generos/', json={'nombre': 'Pagina B C03'})
        assert first.status_code == second.status_code == 201
        p1 = await client.get('/generos/', params={'limit': 1, 'offset': 0})
        p2 = await client.get('/generos/', params={'limit': 1, 'offset': 1})
        assert p1.json()[0]['id'] < p2.json()[0]['id']
        assert (await client.get('/generos/', params={'offset': -1})).status_code == 422
        assert (await client.get('/generos/abc/libros')).status_code == 422
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM genero WHERE nombre IN ('Pagina A C03', 'Pagina B C03')"))
