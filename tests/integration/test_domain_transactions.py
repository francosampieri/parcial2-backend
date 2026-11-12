"""Transacciones completas y recuperacion tras errores de integridad."""
from uuid import uuid4
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

@pytest.mark.asyncio
@pytest.mark.parametrize('tipo', ['libro','venta'])
async def test_operacion_atomica_y_sesion_recuperable(application, tipo):
    token = uuid4().hex
    engine = application.state.engine
    async with engine.begin() as con:
        ed = (await con.execute(text("INSERT INTO editorial(nombre,pais) VALUES(:n,'AR') RETURNING id"), {'n': token})).scalar_one()
        au = (await con.execute(text("INSERT INTO autor(nombre,nacionalidad) VALUES(:n,'AR') RETURNING id"), {'n': token})).scalar_one()
        cli = (await con.execute(text("INSERT INTO cliente(nombre,email) VALUES(:n,:n) RETURNING id"), {'n': token})).scalar_one()
        libro_base = (await con.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id) VALUES(:n,:n,1,0,:e) RETURNING id"), {'n': token, 'e':ed})).scalar_one()
    venta_id = None
    libro_id = None
    try:
        async with application.state.session_factory() as session:
            if tipo == 'libro':
                libro_id = (await session.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id) VALUES(:n,:n,1,0,:e) RETURNING id"), {'n': token+'-new','e':ed})).scalar_one()
                with pytest.raises(IntegrityError):
                    await session.execute(text("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(:l,:a,'invalido',1)"), {'l':libro_id,'a':au})
            else:
                venta_id = (await session.execute(text('INSERT INTO venta(cliente_id,fecha,total) VALUES(:c,CURRENT_TIMESTAMP,0) RETURNING id'), {'c':cli})).scalar_one()
                with pytest.raises(IntegrityError):
                    await session.execute(text('INSERT INTO renglon_venta(venta_id,libro_id,cantidad,precio_unitario) VALUES(:v,:l,0,1)'), {'v':venta_id,'l':libro_base})
            await session.rollback()
            async with engine.connect() as verificacion:
                if tipo == 'libro':
                    assert (await verificacion.execute(text('SELECT count(*) FROM libro WHERE id=:id'), {'id':libro_id})).scalar_one() == 0
                    assert (await verificacion.execute(text('SELECT count(*) FROM libro_autor WHERE libro_id=:id'), {'id':libro_id})).scalar_one() == 0
                else:
                    assert (await verificacion.execute(text('SELECT count(*) FROM venta WHERE id=:id'), {'id':venta_id})).scalar_one() == 0
                    assert (await verificacion.execute(text('SELECT count(*) FROM renglon_venta WHERE venta_id=:id'), {'id':venta_id})).scalar_one() == 0
            if tipo == 'libro':
                libro_id = (await session.execute(text("INSERT INTO libro(isbn,titulo,precio,stock,editorial_id) VALUES(:n,:n,1,0,:e) RETURNING id"), {'n':token+'-new','e':ed})).scalar_one()
                await session.execute(text("INSERT INTO libro_autor(libro_id,autor_id,rol,orden) VALUES(:l,:a,'autor',1)"), {'l':libro_id,'a':au})
            else:
                venta_id = (await session.execute(text('INSERT INTO venta(cliente_id,fecha,total) VALUES(:c,CURRENT_TIMESTAMP,0) RETURNING id'), {'c':cli})).scalar_one()
                await session.execute(text('INSERT INTO renglon_venta(venta_id,libro_id,cantidad,precio_unitario) VALUES(:v,:l,1,1)'), {'v':venta_id,'l':libro_base})
            await session.commit()
        async with engine.connect() as con:
            tabla, columna, valor = ('libro_autor','libro_id',libro_id) if tipo == 'libro' else ('renglon_venta','venta_id',venta_id)
            assert (await con.execute(text(f'SELECT count(*) FROM {tabla} WHERE {columna}=:id'), {'id':valor})).scalar_one() == 1
    finally:
        async with engine.begin() as con:
            if venta_id is not None:
                await con.execute(text('DELETE FROM renglon_venta WHERE venta_id=:id'), {'id':venta_id})
                await con.execute(text('DELETE FROM venta WHERE id=:id'), {'id':venta_id})
            if libro_id is not None:
                await con.execute(text('DELETE FROM libro_autor WHERE libro_id=:id'), {'id':libro_id})
                await con.execute(text('DELETE FROM libro WHERE id=:id'), {'id':libro_id})
            await con.execute(text('DELETE FROM libro WHERE id=:id'), {'id':libro_base})
            await con.execute(text('DELETE FROM autor WHERE id=:id'), {'id':au})
            await con.execute(text('DELETE FROM editorial WHERE id=:id'), {'id':ed})
            await con.execute(text('DELETE FROM cliente WHERE id=:id'), {'id':cli})
