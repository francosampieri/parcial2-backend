"""Verificar superficie HTTP y esquema OpenAPI de catálogo."""
import inspect
import pytest
from fastapi.routing import APIRoute


@pytest.mark.asyncio
async def test_catalogo_operaciones_openapi_y_handlers_async(application, client):
    expected = {
        '/editoriales/': {'get', 'post'}, '/editoriales/{id}': {'get', 'patch'},
        '/editoriales/{id}/libros': {'get'}, '/generos/': {'get', 'post'},
        '/generos/{id}/libros': {'get'}, '/autores/': {'post'},
        '/autores/{id}': {'get', 'patch'}, '/autores/{id}/libros': {'get'},
        '/libros/': {'post', 'get'}, '/libros/{id}': {'get', 'patch'},
    }
    response = await client.get('/openapi.json')
    assert response.status_code == 200
    paths = response.json()['paths']
    assert sum(len(methods) for methods in expected.values()) == 16
    for path, methods in expected.items():
        assert set(paths[path]) == methods
    for route in application.routes:
        if isinstance(route, APIRoute):
            assert inspect.iscoroutinefunction(route.endpoint)
    assert (await client.get('/health/live')).status_code == 200
    assert (await client.get('/health/ready')).status_code == 200
