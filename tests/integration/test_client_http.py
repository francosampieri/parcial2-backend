"""Contratos HTTP de clientes y perfiles en PostgreSQL privado."""
import pytest


def test_openapi_clientes_publica_solo_las_cuatro_rutas_async():
    import inspect

    from app.main import create_app

    application = create_app()
    schema = application.openapi()
    client_operations = {
        (path, method)
        for path, item in schema['paths'].items()
        if path.startswith('/clientes')
        for method in item
        if method in {'get', 'post', 'patch', 'put', 'delete'}
    }
    assert client_operations == {
        ('/clientes/', 'post'),
        ('/clientes/{id}', 'get'),
        ('/clientes/{id}', 'patch'),
        ('/clientes/{id}/perfil', 'post'),
    }
    assert all(
        inspect.iscoroutinefunction(route.endpoint)
        for route in application.routes
        if getattr(route, 'path', '').startswith('/clientes')
    )


@pytest.mark.asyncio
async def test_post_cliente_crea_y_devuelve_id(client, application):
    email = 'crear-c04@example.test'
    try:
        response = await client.post('/clientes/', json={'nombre': 'Franco', 'email': email})
        assert response.status_code == 201
        assert response.json()['id'] > 0
        assert response.json()['nombre'] == 'Franco'
        assert response.json()['email'] == email
    finally:
        from sqlalchemy import text
        async with application.state.engine.begin() as conn:
            await conn.execute(text('DELETE FROM cliente WHERE email = :email'), {'email': email})


@pytest.mark.asyncio
async def test_post_cliente_dos_entradas_generan_ids_distintos(client, application):
    emails = ['uno-c04@example.test', 'dos-c04@example.test']
    try:
        first = await client.post('/clientes/', json={'nombre': 'Uno', 'email': emails[0]})
        second = await client.post('/clientes/', json={'nombre': 'Dos', 'email': emails[1]})
        assert first.status_code == second.status_code == 201
        assert first.json()['id'] != second.json()['id']
    finally:
        from sqlalchemy import text
        async with application.state.engine.begin() as conn:
            await conn.execute(text('DELETE FROM cliente WHERE email = ANY(:emails)'), {'emails': emails})


@pytest.mark.asyncio
@pytest.mark.parametrize('extra', [{'id': 42}, {'campo_desconocido': 'valor'}])
async def test_post_cliente_rechaza_campos_no_declarados(client, application, extra):
    from sqlalchemy import text
    try:
        response = await client.post('/clientes/', json={'nombre': 'Invalido', 'email': 'rechazo-c04@example.test', **extra})
        assert response.status_code == 422
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text("DELETE FROM cliente WHERE email = 'rechazo-c04@example.test'"))


@pytest.mark.asyncio
async def test_email_duplicado_retorna_409_y_sesion_recupera(client, application):
    from sqlalchemy import text
    emails = ['unico-c04@example.test', 'despues-c04@example.test']
    try:
        first = await client.post('/clientes/', json={'nombre': 'Original', 'email': emails[0]})
        assert first.status_code == 201
        conflict = await client.post('/clientes/', json={'nombre': 'Duplicado', 'email': emails[0]})
        assert conflict.status_code == 409
        assert 'INSERT' not in conflict.text and 'UNIQUE' not in conflict.text
        async with application.state.engine.connect() as conn:
            rows = (await conn.execute(text('SELECT nombre FROM cliente WHERE email = :email'), {'email': emails[0]})).scalars().all()
        assert rows == ['Original']
        later = await client.post('/clientes/', json={'nombre': 'Posterior', 'email': emails[1]})
        assert later.status_code == 201
    finally:
        async with application.state.engine.begin() as conn:
            await conn.execute(text('DELETE FROM cliente WHERE email = ANY(:emails)'), {'emails': emails})


@pytest.mark.asyncio
async def test_detalle_cliente_sin_perfil_y_errores(client, client_seed):
    async with client_seed() as seed:
        id_ = await seed('Sin perfil', 'sin-perfil-c04@example.test')
        detail = await client.get(f'/clientes/{id_}')
        assert detail.status_code == 200
        assert detail.json() == {'id': id_, 'nombre': 'Sin perfil', 'email': 'sin-perfil-c04@example.test', 'perfil': None}
        assert (await client.get('/clientes/999999999')).status_code == 404
        assert (await client.get('/clientes/no-entero')).status_code == 422


@pytest.mark.asyncio
async def test_detalle_cliente_con_perfil_precargado(client, client_seed, application):
    from sqlalchemy import event, text
    async with client_seed() as seed:
        id_ = await seed('Con perfil', 'con-perfil-c04@example.test')
        async with application.state.engine.begin() as conn:
            await conn.execute(text("INSERT INTO perfil_cliente (cliente_id, telefono, direccion) VALUES (:id, '123', 'Calle 1')"), {'id': id_})
        statements = []
        def observe(*args):
            statements.append(args[2])
        event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        try:
            response = await client.get(f'/clientes/{id_}')
        finally:
            event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
        assert response.status_code == 200
        assert response.json()['perfil']['telefono'] == '123'
        assert response.json()['perfil']['cliente_id'] == id_
        assert len(statements) == 1


@pytest.mark.asyncio
async def test_patch_cliente_modifica_solo_campos_enviados(client, client_seed, application):
    from sqlalchemy import text
    async with client_seed() as seed:
        id_ = await seed('Nombre inicial', 'inicial-c04@example.test')
        async with application.state.engine.begin() as conn:
            await conn.execute(text("INSERT INTO perfil_cliente (cliente_id, telefono, direccion) VALUES (:id, '444', 'Avenida')"), {'id': id_})
        changed_name = await client.patch(f'/clientes/{id_}', json={'nombre': 'Nuevo nombre'})
        assert changed_name.status_code == 200
        assert changed_name.json()['nombre'] == 'Nuevo nombre'
        assert changed_name.json()['email'] == 'inicial-c04@example.test'
        assert changed_name.json()['perfil']['telefono'] == '444'
        changed_email = await client.patch(f'/clientes/{id_}', json={'email': 'nuevo-c04@example.test'})
        assert changed_email.status_code == 200
        assert changed_email.json()['nombre'] == 'Nuevo nombre'
        assert changed_email.json()['email'] == 'nuevo-c04@example.test'
    assert (await client.patch('/clientes/999999999', json={'nombre': 'X'})).status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize('payload', [{'nombre': None}, {'email': None}, {'inesperado': 'X'}])
async def test_patch_rechaza_null_y_extras_sin_modificar(client, client_seed, payload):
    async with client_seed() as seed:
        id_ = await seed('Estable', 'estable-c04@example.test')
        response = await client.patch(f'/clientes/{id_}', json=payload)
        assert response.status_code == 422
        detail = await client.get(f'/clientes/{id_}')
        assert detail.json()['nombre'] == 'Estable'
        assert detail.json()['email'] == 'estable-c04@example.test'


@pytest.mark.asyncio
async def test_patch_email_duplicado_retorna_409_y_conserva_anterior(client, client_seed):
    async with client_seed() as seed:
        first = await seed('Primero', 'primero-patch-c04@example.test')
        await seed('Segundo', 'segundo-patch-c04@example.test')
        conflict = await client.patch(f'/clientes/{first}', json={'email': 'segundo-patch-c04@example.test'})
        assert conflict.status_code == 409
        assert 'UPDATE' not in conflict.text and 'UNIQUE' not in conflict.text
        detail = await client.get(f'/clientes/{first}')
        assert detail.json()['email'] == 'primero-patch-c04@example.test'


@pytest.mark.asyncio
async def test_post_perfil_crea_objeto_del_cliente(client, client_seed):
    async with client_seed() as seed:
        id_ = await seed('Perfil nuevo', 'perfil-nuevo-c04@example.test')
        response = await client.post(f'/clientes/{id_}/perfil', json={'telefono': '1234', 'direccion': 'Calle 10'})
        assert response.status_code == 201
        assert response.json()['cliente_id'] == id_
        assert response.json()['telefono'] == '1234'
        detail = await client.get(f'/clientes/{id_}')
        assert detail.json()['perfil']['direccion'] == 'Calle 10'


@pytest.mark.asyncio
@pytest.mark.parametrize('extra', [{'id': 50}, {'cliente_id': 77}, {'otro': 'X'}])
async def test_post_perfil_rechaza_campos_no_declarados(client, client_seed, extra):
    async with client_seed() as seed:
        id_ = await seed('Perfil extra', 'perfil-extra-c04@example.test')
        response = await client.post(f'/clientes/{id_}/perfil', json={'telefono': '111', 'direccion': 'Calle', **extra})
        assert response.status_code == 422
        assert (await client.get(f'/clientes/{id_}')).json()['perfil'] is None


@pytest.mark.asyncio
async def test_post_perfil_cliente_ausente_o_datos_incompletos(client, client_seed):
    async with client_seed() as seed:
        id_ = await seed('Perfil faltante', 'perfil-faltante-c04@example.test')
        assert (await client.post(f'/clientes/{id_}/perfil', json={'telefono': '111'})).status_code == 422
        assert (await client.post('/clientes/999999999/perfil', json={'telefono': '111', 'direccion': 'Calle'})).status_code == 404


@pytest.mark.asyncio
async def test_segundo_perfil_409_y_otro_cliente_puede_crear(client, client_seed):
    async with client_seed() as seed:
        first = await seed('Primero', 'primero-perfil-c04@example.test')
        second = await seed('Segundo', 'segundo-perfil-c04@example.test')
        assert (await client.post(f'/clientes/{first}/perfil', json={'telefono': '111', 'direccion': 'Original'})).status_code == 201
        conflict = await client.post(f'/clientes/{first}/perfil', json={'telefono': '222', 'direccion': 'Otra'})
        assert conflict.status_code == 409
        assert 'INSERT' not in conflict.text and 'UNIQUE' not in conflict.text
        detail = await client.get(f'/clientes/{first}')
        assert detail.json()['perfil']['direccion'] == 'Original'
        assert (await client.post(f'/clientes/{second}/perfil', json={'telefono': '333', 'direccion': 'Segunda'})).status_code == 201


@pytest.mark.asyncio
async def test_detalle_perfil_opcional_usa_una_consulta_en_ambos_casos(client, client_seed, application):
    from sqlalchemy import event
    async with client_seed() as seed:
        without = await seed('Sin relación', 'sin-relacion-c04@example.test')
        with_profile = await seed('Con relación', 'con-relacion-c04@example.test')
        assert (await client.post(f'/clientes/{with_profile}/perfil', json={'telefono': '444', 'direccion': 'Calle'})).status_code == 201
        counts = []
        for id_ in (without, with_profile):
            statements = []
            def observe(*args):
                statements.append(args[2])
            event.listen(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            try:
                response = await client.get(f'/clientes/{id_}')
            finally:
                event.remove(application.state.engine.sync_engine, 'before_cursor_execute', observe)
            assert response.status_code == 200
            counts.append(len(statements))
        assert counts == [1, 1]
