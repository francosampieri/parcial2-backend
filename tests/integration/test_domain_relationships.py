"""Relaciones navegables del dominio."""
import pytest
from sqlalchemy import inspect
from app.modules import register_models

@pytest.mark.parametrize(('modulo', 'clase', 'nombres'), [
 ('editoriales', 'Editorial', {'libros'}), ('generos', 'Genero', {'libros'}),
 ('autores', 'Autor', {'autorias'}), ('libros', 'Libro', {'editorial','genero','autorias','renglones_venta'}),
 ('libros', 'LibroAutor', {'libro','autor'}), ('clientes','Cliente',{'perfil','ventas'}),
 ('clientes','PerfilCliente',{'cliente'}), ('ventas','Venta',{'cliente','renglones'}),
 ('ventas','RenglonVenta',{'venta','libro'}),
])
def test_relaciones_bidireccionales_registradas(modulo, clase, nombres):
    from importlib import import_module
    register_models()
    model = getattr(import_module(f'app.modules.{modulo}.models'), clase)
    assert nombres <= set(inspect(model).relationships.keys())

@pytest.mark.asyncio
@pytest.mark.parametrize('cantidad', [1, 2])
async def test_navegacion_catalogo_precargada_sin_sql(domain_session, cantidad):
    from sqlalchemy import event, select
    from sqlalchemy.orm import joinedload, selectinload
    from app.modules.editoriales.models import Editorial
    from app.modules.autores.models import Autor
    from app.modules.libros.models import Libro, LibroAutor
    editorial = Editorial(nombre='Editorial', pais='AR')
    libro = Libro(isbn='1', titulo='Libro', precio='1.00', stock=0, editorial=editorial)
    for i in range(cantidad):
        autor = Autor(nombre=f'Autor {i}', nacionalidad='AR')
        libro.autorias.append(LibroAutor(autor=autor, rol='autor', orden=i+1))
    domain_session.add(libro)
    await domain_session.flush()
    domain_session.expire_all()
    stmt = (select(Libro).options(
        joinedload(Libro.editorial).selectinload(Editorial.libros),
        selectinload(Libro.autorias).joinedload(LibroAutor.autor).selectinload(Autor.autorias),
    ))
    resultado = (await domain_session.execute(stmt)).scalar_one()
    consultas = []
    def registrar(*args): consultas.append(args)
    event.listen(domain_session.bind.sync_engine, 'before_cursor_execute', registrar)
    try:
        assert resultado in resultado.editorial.libros
        assert len(resultado.autorias) == cantidad
        assert all(a in a.autor.autorias for a in resultado.autorias)
        assert sorted(a.orden for a in resultado.autorias) == list(range(1,cantidad+1))
        assert consultas == []
    finally:
        event.remove(domain_session.bind.sync_engine, 'before_cursor_execute', registrar)

@pytest.mark.asyncio
@pytest.mark.parametrize('tiene_perfil', [False, True])
async def test_cliente_perfil_escalar_precargado(domain_session, tiene_perfil):
    from sqlalchemy import event, select
    from sqlalchemy.orm import joinedload
    from app.modules.clientes.models import Cliente, PerfilCliente
    cliente = Cliente(nombre='Cliente', email='cliente@example.test')
    if tiene_perfil:
        cliente.perfil = PerfilCliente(telefono='123', direccion='Calle')
    domain_session.add(cliente)
    await domain_session.flush()
    domain_session.expire_all()
    stmt = select(Cliente).options(joinedload(Cliente.perfil).joinedload(PerfilCliente.cliente))
    resultado = (await domain_session.execute(stmt)).scalar_one()
    consultas = []
    def registrar(*args): consultas.append(args)
    event.listen(domain_session.bind.sync_engine, 'before_cursor_execute', registrar)
    try:
        if tiene_perfil:
            assert resultado.perfil.telefono == '123'
            assert resultado.perfil.cliente is resultado
        else:
            assert resultado.perfil is None
        assert not consultas
    finally:
        event.remove(domain_session.bind.sync_engine, 'before_cursor_execute', registrar)

@pytest.mark.asyncio
@pytest.mark.parametrize('cantidad', [1,2])
async def test_venta_y_renglones_precargados_sin_sql(domain_session, cantidad):
    from datetime import datetime, timezone
    from decimal import Decimal
    from sqlalchemy import event, select
    from sqlalchemy.orm import joinedload, selectinload
    from app.modules.clientes.models import Cliente
    from app.modules.editoriales.models import Editorial
    from app.modules.libros.models import Libro
    from app.modules.ventas.models import Venta, RenglonVenta
    cliente = Cliente(nombre='Cliente', email='ventas@example.test')
    editorial = Editorial(nombre='Editorial', pais='AR')
    venta = Venta(cliente=cliente, fecha=datetime.now(timezone.utc), total=Decimal('4.00'))
    for i in range(cantidad):
        libro = Libro(isbn=f'ISBN-{i}', titulo=f'Libro {i}', precio=Decimal('2.00'), stock=0, editorial=editorial)
        venta.renglones.append(RenglonVenta(libro=libro, cantidad=i+1, precio_unitario=Decimal('2.00')))
    domain_session.add(venta)
    if cantidad == 2:
        domain_session.add(Venta(cliente=cliente, fecha=datetime.now(timezone.utc), total=Decimal('0.00')))
    await domain_session.flush()
    venta_id = venta.id
    domain_session.expire_all()
    stmt = select(Venta).where(Venta.id == venta_id).options(
        joinedload(Venta.cliente).selectinload(Cliente.ventas),
        selectinload(Venta.renglones).joinedload(RenglonVenta.venta),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro).selectinload(Libro.renglones_venta),
    )
    resultado = (await domain_session.execute(stmt)).scalar_one()
    consultas = []
    def registrar(*args): consultas.append(args)
    event.listen(domain_session.bind.sync_engine, 'before_cursor_execute', registrar)
    try:
        assert resultado in resultado.cliente.ventas
        assert len(resultado.cliente.ventas) == cantidad
        assert len(resultado.renglones) == cantidad
        assert all(r.venta is resultado and r in r.libro.renglones_venta for r in resultado.renglones)
        assert {r.cantidad for r in resultado.renglones} == set(range(1,cantidad+1))
        assert all(r.precio_unitario == Decimal('2.00') for r in resultado.renglones)
        assert not consultas
    finally:
        event.remove(domain_session.bind.sync_engine, 'before_cursor_execute', registrar)

@pytest.mark.asyncio
@pytest.mark.parametrize(('genero_presente','rol'), [(False,'autor'),(True,'traductor')])
async def test_genero_opcional_y_roles_precargados(domain_session, genero_presente, rol):
    from decimal import Decimal
    from sqlalchemy import event, select
    from sqlalchemy.orm import joinedload, selectinload
    from app.modules.editoriales.models import Editorial
    from app.modules.generos.models import Genero
    from app.modules.autores.models import Autor
    from app.modules.libros.models import Libro, LibroAutor
    libro = Libro(isbn='tipo',titulo='Titulo',precio=Decimal('1'),stock=0,editorial=Editorial(nombre='e',pais='AR'))
    if genero_presente:
        libro.genero = Genero(nombre='g')
    libro.autorias.append(LibroAutor(autor=Autor(nombre='a',nacionalidad='AR'), rol=rol, orden=1))
    domain_session.add(libro)
    await domain_session.flush()
    domain_session.expire_all()
    stmt=select(Libro).options(joinedload(Libro.genero).selectinload(Genero.libros), selectinload(Libro.autorias).joinedload(LibroAutor.autor))
    encontrado=(await domain_session.execute(stmt)).scalar_one()
    consultas=[]
    def registrar(*args): consultas.append(args)
    event.listen(domain_session.bind.sync_engine,'before_cursor_execute',registrar)
    try:
        if genero_presente:
            assert encontrado in encontrado.genero.libros
        else:
            assert encontrado.genero is None
        assert encontrado.autorias[0].rol == rol and encontrado.autorias[0].autor.nombre == 'a'
        assert not consultas
    finally:
        event.remove(domain_session.bind.sync_engine,'before_cursor_execute',registrar)
