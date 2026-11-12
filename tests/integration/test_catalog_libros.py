"""Alta y consulta de libros por HTTP."""
import pytest
from sqlalchemy import text
from sqlalchemy import event


@pytest.mark.asyncio
async def test_libro_alta_atomica_http(client, application):
    autor_id = editorial_id = None
    try:
        async with application.state.engine.begin() as conn:
            editorial_id = (await conn.execute(text("INSERT INTO editorial(nombre,pais) VALUES ('Libros Editorial C03','AR') RETURNING id"))).scalar_one()
            autor_id = (await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES ('Libros Autor C03','AR') RETURNING id"))).scalar_one()
        data = {'isbn': 'libro-c03-uno', 'titulo': 'Libro C03', 'precio': '1.23', 'stock': 1, 'editorial_id': editorial_id, 'autores': [{'autor_id': autor_id, 'rol': 'autor', 'orden': 1}]}
        response = await client.post('/libros/', json=data)
        assert response.status_code == 201
        assert response.json()['isbn'] == 'libro-c03-uno'
        assert response.json()['autores'][0]['autor']['id'] == autor_id
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM libro_autor WHERE libro_id IN (SELECT id FROM libro WHERE isbn='libro-c03-uno')"))
            await conn.execute(text("DELETE FROM libro WHERE isbn='libro-c03-uno'"))
            if autor_id:
                await conn.execute(text("DELETE FROM autor WHERE id=:id"), {'id': autor_id})
            if editorial_id:
                await conn.execute(text("DELETE FROM editorial WHERE id=:id"), {'id': editorial_id})


@pytest.mark.asyncio
async def test_libro_autorias_multiples_validacion_rollback_y_sin_preconsulta(client, application):
    try:
        async with application.state.engine.begin() as conn:
            editorial = (await conn.execute(text("INSERT INTO editorial(nombre,pais) VALUES ('Libro multi ed C03','AR') RETURNING id"))).scalar_one()
            genero = (await conn.execute(text("INSERT INTO genero(nombre) VALUES ('Libro multi genero C03') RETURNING id"))).scalar_one()
            a1 = (await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES ('Libro multi A C03','AR') RETURNING id"))).scalar_one()
            a2 = (await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES ('Libro multi B C03','UY') RETURNING id"))).scalar_one()
        data = {'isbn':'multi-c03','titulo':'Multi C03','precio':'25.00','stock':0,'editorial_id':editorial,'genero_id':genero,'autores':[{'autor_id':a1,'rol':'autor','orden':1},{'autor_id':a2,'rol':'coautor','orden':1}]}
        statements=[]
        def observe(*args):
            statements.append(args[2])
        event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        try:
            response = await client.post('/libros/', json=data)
        finally:
            event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        assert response.status_code == 201
        assert len(response.json()['autores']) == 2
        assert response.json()['genero']['id'] == genero
        assert statements[0].lstrip().upper().startswith('INSERT')
        for updates in ({'autores': []}, {'precio':'1.234'}, {'precio':'0'}, {'precio':'-1'}, {'precio':'100000000.00'}, {'stock': -1}, {'id': 1}, {'autores':[{'autor_id':a1,'rol':'autor','orden':1,'extra':0}]}, {'autores':[{'autor_id':a1,'rol':'otro','orden':1}]}, {'autores':[{'autor_id':a1,'rol':'autor','orden':0}]}):
            assert (await client.post('/libros/', json={**data, **updates})).status_code == 422
        for updates in ({'isbn':'fk-editorial-c03','editorial_id':999999999}, {'isbn':'fk-genero-c03','genero_id':999999999}, {'isbn':'fk-autor-c03','autores':[{'autor_id':999999999,'rol':'autor','orden':1}]}, {'isbn':'duplicado-autor-c03','autores':[{'autor_id':a1,'rol':'autor','orden':1},{'autor_id':a1,'rol':'autor','orden':2}]}, {}):
            result = await client.post('/libros/', json={**data, **updates})
            assert result.status_code == 409
            assert 'INSERT' not in result.text
        async with application.state.engine.connect() as conn:
            count = (await conn.execute(text("SELECT count(*) FROM libro WHERE isbn IN ('fk-editorial-c03','fk-genero-c03','fk-autor-c03','duplicado-autor-c03')"))).scalar_one()
            assert count == 0
        recovered = await client.post('/libros/', json={**data, 'isbn': 'recuperado-c03', 'precio': '0.01'})
        assert recovered.status_code == 201
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM libro_autor WHERE libro_id IN (SELECT id FROM libro WHERE isbn IN ('multi-c03','fk-editorial-c03','fk-genero-c03','fk-autor-c03','duplicado-autor-c03','recuperado-c03'))"))
            await conn.execute(text("DELETE FROM libro WHERE isbn IN ('multi-c03','fk-editorial-c03','fk-genero-c03','fk-autor-c03','duplicado-autor-c03','recuperado-c03')"))
            await conn.execute(text("DELETE FROM autor WHERE nombre IN ('Libro multi A C03','Libro multi B C03')"))
            await conn.execute(text("DELETE FROM genero WHERE nombre='Libro multi genero C03'"))
            await conn.execute(text("DELETE FROM editorial WHERE nombre='Libro multi ed C03'"))


@pytest.mark.asyncio
async def test_listar_libros_busqueda_literal_y_paginacion(client, application):
    try:
        async with application.state.engine.begin() as conn:
            editorial = (await conn.execute(text("INSERT INTO editorial(nombre,pais) VALUES ('Lista libro Ed C03','AR') RETURNING id"))).scalar_one()
            genre = (await conn.execute(text("INSERT INTO genero(nombre) VALUES ('Lista libro Gen C03') RETURNING id"))).scalar_one()
            for n,title in enumerate(['Cien % libros','Cien _ libros','Otro libro'], 1):
                await conn.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id,genero_id) VALUES (:isbn,:title,10,1,:editorial,:genre)"), {'isbn':f'lista-c03-{n}', 'title':title,'editorial':editorial,'genre':genre})
        response = await client.get('/libros/', params={'titulo':'CIEN %', 'genero_id':genre})
        assert response.status_code == 200
        assert [item['titulo'] for item in response.json()] == ['Cien % libros']
        assert response.json()[0]['editorial']['id'] == editorial
        assert response.json()[0]['genero']['id'] == genre
        underscore = await client.get('/libros/', params={'titulo':'cien _', 'genero_id':genre})
        assert [item['titulo'] for item in underscore.json()] == ['Cien _ libros']
        statements = []
        def observe(conn, cursor, statement, parameters, context, executemany):
            statements.append((statement, parameters))
        event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        try:
            assert (await client.get('/libros/', params={'titulo':"' OR '1'='1"})).json() == []
            assert "' OR '1'='1" not in statements[0][0]
            assert any("' OR '1'='1" in str(parameter) for parameter in statements[0][1])
        finally:
            event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        page = await client.get('/libros/', params={'genero_id':genre,'limit':1,'offset':1})
        assert page.json()[0]['titulo'] == 'Cien _ libros'
        for params in ({'limit':0},{'limit':101},{'offset':-1},{'genero_id':'abc'}):
            assert (await client.get('/libros/', params=params)).status_code == 422
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM libro WHERE isbn IN ('lista-c03-1','lista-c03-2','lista-c03-3')"))
            await conn.execute(text("DELETE FROM genero WHERE nombre='Lista libro Gen C03'"))
            await conn.execute(text("DELETE FROM editorial WHERE nombre='Lista libro Ed C03'"))


@pytest.mark.asyncio
async def test_detalle_libro_sin_n_mas_uno(client, application):
    try:
        async with application.state.engine.begin() as conn:
            ed = (await conn.execute(text("INSERT INTO editorial(nombre,pais) VALUES ('Detalle ed C03','AR') RETURNING id"))).scalar_one()
            gen = (await conn.execute(text("INSERT INTO genero(nombre) VALUES ('Detalle gen C03') RETURNING id"))).scalar_one()
            author_ids = [(await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES (:nombre,'AR') RETURNING id"), {'nombre':f'Detalle autor C03 {n}'})).scalar_one() for n in (1,2,3)]
            ids = []
            for n in (1,2):
                book = (await conn.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id,genero_id) VALUES (:isbn,'Detalle',10,1,:ed,:gen) RETURNING id"), {'isbn':f'detalle-c03-{n}','ed':ed,'gen':gen if n == 2 else None})).scalar_one()
                ids.append(book)
                for author in author_ids[:1 if n == 1 else 3]:
                    await conn.execute(text("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES (:book,:author,'autor',1)"), {'book':book,'author':author})
        counts=[]
        for book_id in ids:
            statements=[]
            def observe(*args):
                statements.append(args[2])
            event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            try:
                response = await client.get(f'/libros/{book_id}')
            finally:
                event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            assert response.status_code == 200
            data=response.json()
            assert data['editorial']['id'] == ed
            assert len(data['autores']) in (1,3)
            assert [a['autor']['id'] for a in data['autores']] == sorted(a['autor']['id'] for a in data['autores'])
            assert all(a['rol'] == 'autor' and a['orden'] == 1 for a in data['autores'])
            assert (data['genero'] is None) == (book_id == ids[0])
            counts.append(len(statements))
        assert counts == [2, 2]
        assert (await client.get('/libros/999999999')).status_code == 404
        assert (await client.get('/libros/no-entero')).status_code == 422
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM libro_autor WHERE libro_id IN (SELECT id FROM libro WHERE isbn IN ('detalle-c03-1','detalle-c03-2'))"))
            await conn.execute(text("DELETE FROM libro WHERE isbn IN ('detalle-c03-1','detalle-c03-2')"))
            await conn.execute(text("DELETE FROM autor WHERE nombre LIKE 'Detalle autor C03 %'"))
            await conn.execute(text("DELETE FROM genero WHERE nombre='Detalle gen C03'"))
            await conn.execute(text("DELETE FROM editorial WHERE nombre='Detalle ed C03'"))


@pytest.mark.asyncio
async def test_patch_libro_preserva_omite_y_valida(client, application):
    try:
        async with application.state.engine.begin() as conn:
            ed = (await conn.execute(text("INSERT INTO editorial(nombre,pais) VALUES ('Patch libro ed C03','AR') RETURNING id"))).scalar_one()
            gen = (await conn.execute(text("INSERT INTO genero(nombre) VALUES ('Patch libro gen C03') RETURNING id"))).scalar_one()
            author = (await conn.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES ('Patch libro autor C03','AR') RETURNING id"))).scalar_one()
            book = (await conn.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id,genero_id) VALUES ('patch-c03-1','Original',10,1,:ed,:gen) RETURNING id"), {'ed':ed,'gen':gen})).scalar_one()
            await conn.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id) VALUES ('patch-c03-2','Otro',10,1,:ed)"), {'ed':ed})
            await conn.execute(text("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES (:book,:author,'autor',1)"), {'book':book,'author':author})
        changed = await client.patch(f'/libros/{book}', json={'titulo':'Cambiado'})
        assert changed.status_code == 200
        assert changed.json()['isbn'] == 'patch-c03-1'
        assert changed.json()['autores'][0]['autor']['id'] == author
        removed = await client.patch(f'/libros/{book}', json={'genero_id':None})
        assert removed.status_code == 200 and removed.json()['genero'] is None
        for data in ({'titulo':None}, {'precio':None}, {'precio':'1.234'}, {'stock':None}, {'editorial_id':None}, {'isbn':None}, {'autores':[]}, {'otro':1}):
            assert (await client.patch(f'/libros/{book}', json=data)).status_code == 422
        for data in ({'isbn':'patch-c03-2'}, {'editorial_id':999999999}, {'genero_id':999999999}):
            result = await client.patch(f'/libros/{book}', json=data)
            assert result.status_code == 409 and 'UPDATE' not in result.text
        final = (await client.get(f'/libros/{book}')).json()
        assert final['titulo'] == 'Cambiado' and final['isbn'] == 'patch-c03-1'
        assert (await client.patch('/libros/999999999', json={'titulo':'No'})).status_code == 404
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM libro_autor WHERE libro_id IN (SELECT id FROM libro WHERE isbn IN ('patch-c03-1','patch-c03-2'))"))
            await conn.execute(text("DELETE FROM libro WHERE isbn IN ('patch-c03-1','patch-c03-2')"))
            await conn.execute(text("DELETE FROM autor WHERE nombre='Patch libro autor C03'"))
            await conn.execute(text("DELETE FROM genero WHERE nombre='Patch libro gen C03'"))
            await conn.execute(text("DELETE FROM editorial WHERE nombre='Patch libro ed C03'"))
