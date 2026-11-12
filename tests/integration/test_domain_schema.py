"""Esquema persistente de los modelos del dominio."""
import pytest
from sqlalchemy import inspect

@pytest.mark.asyncio
async def test_editorial_registrada_con_columnas(application):
    async with application.state.engine.connect() as connection:
        tables = await connection.run_sync(lambda conn: inspect(conn).get_table_names())
    assert 'editorial' in tables

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla', 'columnas'), [
    ('editorial', {'id', 'nombre', 'pais'}),
    ('genero', {'id', 'nombre'}),
    ('autor', {'id', 'nombre', 'nacionalidad'}),
    ('libro', {'id', 'isbn', 'titulo', 'precio', 'stock', 'editorial_id', 'genero_id'}),
    ('libro_autor', {'libro_id', 'autor_id', 'rol', 'orden'}),
    ('cliente', {'id', 'nombre', 'email'}),
    ('perfil_cliente', {'id', 'cliente_id', 'telefono', 'direccion'}),
    ('venta', {'id', 'cliente_id', 'fecha', 'total'}),
    ('renglon_venta', {'id', 'venta_id', 'libro_id', 'cantidad', 'precio_unitario'}),
])
async def test_columnas_de_tablas_en_postgresql(application, tabla, columnas):
    async with application.state.engine.connect() as connection:
        tables = await connection.run_sync(lambda conn: inspect(conn).get_table_names())
        assert tabla in tables
        actual = await connection.run_sync(lambda conn: inspect(conn).get_columns(tabla))
    assert {col['name'] for col in actual} == columnas

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla', 'columna', 'precision', 'escala'), [
    ('libro', 'precio', 10, 2), ('venta', 'total', 12, 2),
    ('renglon_venta', 'precio_unitario', 10, 2),
])
async def test_importes_tienen_precision_fija(application, tabla, columna, precision, escala):
    async with application.state.engine.connect() as connection:
        cols = await connection.run_sync(lambda conn: inspect(conn).get_columns(tabla))
    tipo = next(c['type'] for c in cols if c['name'] == columna)
    assert (tipo.precision, tipo.scale) == (precision, escala)

@pytest.mark.asyncio
async def test_fecha_venta_almacena_zona_horaria(application):
    async with application.state.engine.connect() as connection:
        cols = await connection.run_sync(lambda conn: inspect(conn).get_columns('venta'))
    assert next(c['type'] for c in cols if c['name'] == 'fecha').timezone

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla','columna'), [
 ('libro','editorial_id'), ('libro','genero_id'), ('libro_autor','libro_id'),
 ('libro_autor','autor_id'), ('perfil_cliente','cliente_id'), ('venta','cliente_id'),
 ('renglon_venta','venta_id'), ('renglon_venta','libro_id'),
])
async def test_fk_tiene_indice_de_prefijo(application, tabla, columna):
    def indices(conn):
        schema = inspect(conn)
        return (schema.get_indexes(tabla), schema.get_pk_constraint(tabla), schema.get_unique_constraints(tabla))
    async with application.state.engine.connect() as connection:
        indexes, pk, uniques = await connection.run_sync(indices)
    candidates = [i['column_names'] for i in indexes] + [pk['constrained_columns']] + [u['column_names'] for u in uniques]
    assert any(cols and cols[0] == columna for cols in candidates)

@pytest.mark.asyncio
async def test_ids_generados_y_genero_ausente(domain_session):
    from decimal import Decimal
    from app.modules.editoriales.models import Editorial
    from app.modules.clientes.models import Cliente
    from app.modules.libros.models import Libro
    editorial = Editorial(nombre='Editor', pais='AR')
    cliente = Cliente(nombre='Cliente', email='id@example.test')
    libro = Libro(isbn='ISBN-ID', titulo='Titulo', precio=Decimal('1.00'), stock=0, editorial=editorial)
    domain_session.add_all([libro,cliente])
    await domain_session.flush()
    assert editorial.id is not None and cliente.id is not None and libro.id is not None
    assert libro.genero_id is None

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla','columna'), [('libro_autor','libro_id'),('perfil_cliente','cliente_id')])
async def test_fk_reutiliza_indice_existente_sin_duplicarlo(application, tabla, columna):
    async with application.state.engine.connect() as conn:
        indices = await conn.run_sync(lambda c: inspect(c).get_indexes(tabla))
    adicionales = [i for i in indices if i['column_names'] == [columna] and not i.get('duplicates_constraint')]
    assert not adicionales

@pytest.mark.asyncio
@pytest.mark.parametrize(('importe','total'), [('0.01','0.00'), ('0.10','0.10'), ('99999999.99','9999999999.99')])
async def test_decimales_exactos_y_limites(domain_session, importe, total):
    from decimal import Decimal
    from sqlalchemy import text
    from sqlalchemy.exc import DBAPIError
    await domain_session.execute(text("INSERT INTO editorial(id,nombre,pais) VALUES(1,'edit','AR')"))
    await domain_session.execute(text("INSERT INTO cliente(id,nombre,email) VALUES(1,'cliente','correo')"))
    await domain_session.execute(text("INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id) VALUES(1,'i','t',:precio,0,1)"), {'precio': Decimal(importe)})
    await domain_session.execute(text("INSERT INTO venta(id,cliente_id,fecha,total) VALUES(1,1,CURRENT_TIMESTAMP,:total)"), {'total': Decimal(total)})
    await domain_session.execute(text("INSERT INTO renglon_venta(id,venta_id,libro_id,cantidad,precio_unitario) VALUES(1,1,1,1,:precio)"), {'precio': Decimal(importe)})
    for tabla, col, expected in [('libro','precio',importe), ('venta','total',total), ('renglon_venta','precio_unitario',importe)]:
        assert (await domain_session.execute(text(f'SELECT {col} FROM {tabla}'))).scalar_one() == Decimal(expected)
    for tabla, col, invalido in [('libro','precio','100000000.00'), ('venta','total','10000000000.00'), ('renglon_venta','precio_unitario','100000000.00')]:
        with pytest.raises(DBAPIError) as error:
            async with domain_session.begin_nested():
                await domain_session.execute(text(f'UPDATE {tabla} SET {col} = :v'), {'v': Decimal(invalido)})
        assert error.value.orig.sqlstate == '22003'

@pytest.mark.asyncio
@pytest.mark.parametrize('offset', [0, -3])
async def test_fecha_conserva_instante_con_offset(domain_session, offset):
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import text
    instante = datetime(2026, 5, 1, 12, 30, tzinfo=timezone(timedelta(hours=offset)))
    await domain_session.execute(text("INSERT INTO cliente(id,nombre,email) VALUES(1,'c','mail')"))
    await domain_session.execute(text("INSERT INTO venta(id,cliente_id,fecha,total) VALUES(1,1,:fecha,0)"), {'fecha': instante})
    guardado = (await domain_session.execute(text('SELECT fecha FROM venta'))).scalar_one()
    assert guardado.tzinfo is not None and guardado == instante

@pytest.mark.asyncio
async def test_persistencia_y_lectura_de_nueve_entidades(domain_session):
    from sqlalchemy import text
    for sql in [
      "INSERT INTO editorial(id,nombre,pais) VALUES(1,'e','AR')",
      "INSERT INTO genero(id,nombre) VALUES(1,'g')",
      "INSERT INTO autor(id,nombre,nacionalidad) VALUES(1,'a','AR')",
      "INSERT INTO cliente(id,nombre,email) VALUES(1,'c','mail')",
      "INSERT INTO perfil_cliente(id,cliente_id,telefono,direccion) VALUES(1,1,'t','d')",
      "INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id,genero_id) VALUES(1,'i','t',1,0,1,1)",
      "INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(1,1,'autor',1)",
      "INSERT INTO venta(id,cliente_id,fecha,total) VALUES(1,1,CURRENT_TIMESTAMP,0)",
      "INSERT INTO renglon_venta(id,venta_id,libro_id,cantidad,precio_unitario) VALUES(1,1,1,1,1)",
    ]:
        await domain_session.execute(text(sql))
    esperado = {'editorial':'e', 'genero':'g', 'autor':'a', 'cliente':'c', 'perfil_cliente':'t', 'libro':'i', 'libro_autor':'autor', 'venta':0, 'renglon_venta':1}
    columna = {'editorial':'nombre', 'genero':'nombre', 'autor':'nombre', 'cliente':'nombre', 'perfil_cliente':'telefono', 'libro':'isbn', 'libro_autor':'rol', 'venta':'total', 'renglon_venta':'cantidad'}
    for tabla, valor in esperado.items():
        assert (await domain_session.execute(text(f'SELECT {columna[tabla]} FROM {tabla}'))).scalar_one() == valor
