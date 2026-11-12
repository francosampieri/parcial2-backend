"""Contratos de entrada de ventas separados de las tablas."""
import pytest
from pydantic import ValidationError


def _venta(**overrides):
    base = {'cliente_id': 1, 'renglones': [{'libro_id': 1, 'cantidad': 2}]}
    base.update(overrides)
    return base


def test_venta_acepta_uno_y_varios_renglones_validos():
    from app.modules.ventas.schemas import VentaCreate

    one = VentaCreate(**_venta())
    two = VentaCreate(**_venta(renglones=[
        {'libro_id': 1, 'cantidad': 2},
        {'libro_id': 4, 'cantidad': 1},
    ]))
    assert one.renglones[0].cantidad == 2
    assert [item.libro_id for item in two.renglones] == [1, 4]


@pytest.mark.parametrize('renglones', [[], [{'libro_id': 1, 'cantidad': 1}, {'libro_id': 1, 'cantidad': 3}]])
def test_venta_rechaza_lista_vacia_o_libro_repetido(renglones):
    from app.modules.ventas.schemas import VentaCreate

    with pytest.raises(ValidationError):
        VentaCreate(**_venta(renglones=renglones))


@pytest.mark.parametrize('cantidad', [0, -1])
def test_renglon_rechaza_cantidad_no_positiva(cantidad):
    from app.modules.ventas.schemas import RenglonCreate

    with pytest.raises(ValidationError):
        RenglonCreate(libro_id=1, cantidad=cantidad)


@pytest.mark.parametrize('campo, valor', [
    ('precio_unitario', '10.00'),
    ('subtotal', '20.00'),
    ('total', '20.00'),
    ('fecha', '2026-11-12T10:00:00Z'),
    ('id', 1),
    ('desconocido', 1),
])
def test_venta_rechaza_campos_calculados_o_desconocidos(campo, valor):
    from app.modules.ventas.schemas import VentaCreate

    with pytest.raises(ValidationError):
        VentaCreate(**_venta(**{campo: valor}))


@pytest.mark.parametrize('campo', ['precio_unitario', 'subtotal', 'id', 'venta_id', 'titulo'])
def test_renglon_rechaza_campos_no_declarados(campo):
    from app.modules.ventas.schemas import RenglonCreate

    with pytest.raises(ValidationError):
        RenglonCreate(libro_id=1, cantidad=1, **{campo: 1})
