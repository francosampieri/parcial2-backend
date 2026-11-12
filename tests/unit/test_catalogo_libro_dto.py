"""Contratos de entrada de libros, independientes de HTTP y DB."""
import pytest
from pydantic import ValidationError


def input_libro(**updates):
    return {'isbn': 'isbn-c03', 'titulo': 'Título', 'precio': '1.23', 'stock': 0, 'editorial_id': 1, 'autores': [{'autor_id': 1, 'rol': 'autor', 'orden': 1}], **updates}


def test_libro_create_acepta_autorias():
    from app.modules.libros.schemas import LibroCreate
    assert len(LibroCreate.model_validate(input_libro()).autores) == 1


def test_libro_create_varias_autorias_y_roles():
    from app.modules.libros.schemas import LibroCreate
    authors = [{'autor_id': n, 'rol': rol, 'orden': n} for n, rol in enumerate(['autor', 'coautor', 'traductor', 'ilustrador'], 1)]
    assert len(LibroCreate.model_validate(input_libro(autores=authors)).autores) == 4


@pytest.mark.parametrize('updates', [
    {'autores': []}, {'id': 3}, {'autores': [{'autor_id': 1, 'rol': 'autor', 'orden': 1, 'extra': 2}]},
    {'autores': [{'autor_id': 1, 'rol': 'otro', 'orden': 1}]},
    {'autores': [{'autor_id': 1, 'rol': 'autor', 'orden': 0}]},
])
def test_libro_create_rechaza_autorias_invalidas(updates):
    from app.modules.libros.schemas import LibroCreate
    with pytest.raises(ValidationError):
        LibroCreate.model_validate(input_libro(**updates))


@pytest.mark.parametrize('price', ['0.01', '1.23', '99999999.99'])
def test_precio_valido(price):
    from decimal import Decimal
    from app.modules.libros.schemas import LibroCreate
    assert LibroCreate.model_validate(input_libro(precio=price)).precio == Decimal(price)


@pytest.mark.parametrize('updates', [{'precio': '0'}, {'precio': '-1'}, {'precio': '1.234'}, {'precio': '100000000.00'}, {'stock': -1}])
def test_precio_stock_invalidos(updates):
    from app.modules.libros.schemas import LibroCreate
    with pytest.raises(ValidationError):
        LibroCreate.model_validate(input_libro(**updates))
