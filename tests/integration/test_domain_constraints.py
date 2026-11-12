"""Restricciones fisicas verificadas con escrituras reales en PostgreSQL."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla', 'columna', 'invalido'), [
    ('libro', 'precio', '0'), ('libro', 'precio', '-1'), ('libro', 'stock', '-1'),
    ('libro_autor', 'orden', '0'), ('libro_autor', 'orden', '-1'), ('libro_autor', 'rol', "'desconocido'"),
    ('venta', 'total', '-1'), ('renglon_venta', 'cantidad', '0'), ('renglon_venta', 'cantidad', '-1'),
    ('renglon_venta', 'precio_unitario', '0'), ('renglon_venta', 'precio_unitario', '-1'),
])
async def test_check_rechaza_valores_fuera_del_dominio(domain_session, tabla, columna, invalido):
    inserts = [
      "INSERT INTO editorial (id,nombre,pais) VALUES (1,'edit','AR')",
      "INSERT INTO genero (id,nombre) VALUES (1,'genero')",
      "INSERT INTO autor (id,nombre,nacionalidad) VALUES (1,'autor','AR')",
      "INSERT INTO cliente (id,nombre,email) VALUES (1,'cliente','correo')",
      "INSERT INTO libro (id,isbn,titulo,precio,stock,editorial_id,genero_id) VALUES (1,'isbn','titulo',1,0,1,1)",
      "INSERT INTO libro_autor (libro_id,autor_id,rol,orden) VALUES (1,1,'autor',1)",
      "INSERT INTO venta (id,cliente_id,fecha,total) VALUES (1,1,CURRENT_TIMESTAMP,0)",
      "INSERT INTO renglon_venta (id,venta_id,libro_id,cantidad,precio_unitario) VALUES (1,1,1,1,1)",
    ]
    for sql in inserts:
        await domain_session.execute(text(sql))
    with pytest.raises(IntegrityError):
        async with domain_session.begin_nested():
            await domain_session.execute(text(f'UPDATE {tabla} SET {columna} = {invalido}'))

@pytest.mark.asyncio
@pytest.mark.parametrize(('primero', 'duplicado'), [
 ("INSERT INTO editorial(id,nombre,pais) VALUES(1,'e','AR')", "INSERT INTO editorial(id,nombre,pais) VALUES(2,'e','UY')"),
 ("INSERT INTO genero(id,nombre) VALUES(1,'g')", "INSERT INTO genero(id,nombre) VALUES(2,'g')"),
 ("INSERT INTO cliente(id,nombre,email) VALUES(1,'c','x')", "INSERT INTO cliente(id,nombre,email) VALUES(2,'d','x')"),
 ("INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id) VALUES(1,'i','t',1,0,1)", "INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id) VALUES(2,'i','u',1,0,1)"),
 ("INSERT INTO perfil_cliente(id,cliente_id,telefono,direccion) VALUES(1,1,'a','b')", "INSERT INTO perfil_cliente(id,cliente_id,telefono,direccion) VALUES(2,1,'c','d')"),
 ("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(1,1,'autor',1)", "INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(1,1,'coautor',2)"),
])
async def test_unicidad_fisica(domain_session, primero, duplicado):
    # Dependencias auxiliares validas para las futuras FK.
    if 'INTO libro(' in primero:
        await domain_session.execute(text("INSERT INTO editorial(id,nombre,pais) VALUES(1,'aux','AR')"))
    if 'INTO perfil_cliente' in primero:
        await domain_session.execute(text("INSERT INTO cliente(id,nombre,email) VALUES(1,'aux','aux')"))
    if 'INTO libro_autor' in primero:
        await domain_session.execute(text("INSERT INTO editorial(id,nombre,pais) VALUES(1,'aux','AR')"))
        await domain_session.execute(text("INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id) VALUES(1,'aux','aux',1,0,1)"))
        await domain_session.execute(text("INSERT INTO autor(id,nombre,nacionalidad) VALUES(1,'aux','AR')"))
    await domain_session.execute(text(primero))
    with pytest.raises(IntegrityError):
        async with domain_session.begin_nested():
            await domain_session.execute(text(duplicado))

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla', 'columna'), [
 ('libro','editorial_id'), ('libro','genero_id'), ('libro_autor','libro_id'),
 ('libro_autor','autor_id'), ('perfil_cliente','cliente_id'), ('venta','cliente_id'),
 ('renglon_venta','venta_id'), ('renglon_venta','libro_id'),
])
async def test_fk_rechaza_referencia_inexistente(domain_session, tabla, columna):
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
    with pytest.raises(IntegrityError):
        async with domain_session.begin_nested():
            await domain_session.execute(text(f'UPDATE {tabla} SET {columna} = 999'))

@pytest.mark.asyncio
@pytest.mark.parametrize(('tabla','columna'), [
 ('editorial','id'), ('editorial','nombre'), ('editorial','pais'), ('genero','id'), ('genero','nombre'),
 ('autor','id'), ('autor','nombre'), ('autor','nacionalidad'), ('libro','id'), ('libro','isbn'),
 ('libro','titulo'), ('libro','precio'), ('libro','stock'), ('libro','editorial_id'),
 ('libro_autor','libro_id'), ('libro_autor','autor_id'), ('libro_autor','rol'), ('libro_autor','orden'),
 ('cliente','id'), ('cliente','nombre'), ('cliente','email'), ('perfil_cliente','id'),
 ('perfil_cliente','cliente_id'), ('perfil_cliente','telefono'), ('perfil_cliente','direccion'),
 ('venta','id'), ('venta','cliente_id'), ('venta','fecha'), ('venta','total'),
 ('renglon_venta','id'), ('renglon_venta','venta_id'), ('renglon_venta','libro_id'),
 ('renglon_venta','cantidad'), ('renglon_venta','precio_unitario'),
])
async def test_columna_obligatoria_rechaza_null(domain_session, tabla, columna):
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
    with pytest.raises(IntegrityError):
        async with domain_session.begin_nested():
            await domain_session.execute(text(f'UPDATE {tabla} SET {columna} = NULL'))

@pytest.mark.asyncio
@pytest.mark.parametrize('rol', ['autor','coautor','traductor','ilustrador'])
async def test_roles_de_autoria_admitidos(domain_session, rol):
    for sql in [
      "INSERT INTO editorial(id,nombre,pais) VALUES(1,'e','AR')",
      "INSERT INTO autor(id,nombre,nacionalidad) VALUES(1,'a','AR')",
      "INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id) VALUES(1,'i','t',0.01,0,1)",
    ]:
        await domain_session.execute(text(sql))
    await domain_session.execute(text('INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(1,1,:rol,1)'), {'rol':rol})
    assert (await domain_session.execute(text('SELECT rol FROM libro_autor'))).scalar_one() == rol

@pytest.mark.asyncio
async def test_valores_distintos_y_mismo_orden_son_validos(domain_session):
    for sql in [
      "INSERT INTO editorial(id,nombre,pais) VALUES(1,'e1','AR'),(2,'e2','UY')",
      "INSERT INTO genero(id,nombre) VALUES(1,'g1'),(2,'g2')",
      "INSERT INTO autor(id,nombre,nacionalidad) VALUES(1,'a','AR'),(2,'b','UY')",
      "INSERT INTO cliente(id,nombre,email) VALUES(1,'c','a'),(2,'d','b')",
      "INSERT INTO perfil_cliente(id,cliente_id,telefono,direccion) VALUES(1,1,'t','d'),(2,2,'t','d')",
      "INSERT INTO libro(id,isbn,titulo,precio,stock,editorial_id) VALUES(1,'i','t',1,0,1),(2,'j','t',1,0,2)",
      "INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(1,1,'autor',1),(1,2,'coautor',1),(2,1,'autor',1)",
    ]:
        await domain_session.execute(text(sql))
    assert (await domain_session.execute(text('SELECT count(*) FROM libro_autor'))).scalar_one() == 3
    assert (await domain_session.execute(text('SELECT count(*) FROM perfil_cliente'))).scalar_one() == 2
