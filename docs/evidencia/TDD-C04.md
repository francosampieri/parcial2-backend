# Evidencia TDD C-04

## Línea de base

Antes de editar código existente, `python -m pytest -q` con PostgreSQL privado pasó **205 pruebas en 73,83 s**. El primer intento dentro del sandbox no llegó a probar la aplicación: `initdb` agotó 90 s; la ejecución acotada con acceso al proceso local permitió obtener la referencia válida.

## Ciclos

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1 | suite previa | integración PostgreSQL | 205/205 | No aplica | 205/205 | No aplica | No aplica |
| 1.2 | tests/integration/test_client_isolation.py | integración PostgreSQL | 205/205 | 2 errores por fixture ausente | 2/2 | cliente ajeno y bloques consecutivos | Sin refactor |
| 2.1 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | POST 404; extras 201 en 2 casos | 4/4 | dos clientes/IDs, ID extra y campo desconocido | Sin refactor |
| 2.2 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | IntegrityError al duplicar email | 5/5 | duplicado rechazado, fila intacta y nueva alta válida | Sin refactor |
| 2.3 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | GET existente 404 | 2/2 detalle | sin perfil/con perfil, 404/422 y una consulta con precarga | Sin refactor |
| 3.1 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | PATCH existente 405 | 1/1 | nombre/email por separado, omitidos/perfil conservados y 404 | Sin refactor |
| 3.2 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | 4 fallos: null a DB, extra aceptado, duplicado IntegrityError | 12/12 conjunto | nombre/email null, extra, email duplicado y fila previa intacta | Relectura POST con joinedload: 12/12 verde |
| 2.4 | README.md | documentación cotejada con HTTP | 205/205 | No aplica | Rutas y respuestas cotejadas con pruebas verdes | alta, detalle, perfil opcional y distinción de autenticación | Sin refactor |
| 3.3 | README.md | documentación cotejada con HTTP | 205/205 | No aplica | Contrato PATCH cotejado con pruebas verdes | omitido, null, 404/409/422 | Sin refactor |
| 4.1 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | POST perfil 404; tres extras aceptados | 5 casos perfil verdes | 201, perfil en detalle, 404, 422 por extras e incompleto | Sin refactor |
| 4.2 | tests/integration/test_client_http.py | HTTP + PostgreSQL | 205/205 | segundo perfil produjo IntegrityError | conjunto C-04 18/18 | primer perfil intacto y creación posterior en otro cliente | Sin refactor |
| 4.3 | tests/integration/test_client_http.py; README.md | HTTP + SQL contabilizado | 205/205 | No aplica: verifica precarga implementada en 2.3 | 1/1 | sin/con perfil: [1, 1] consultas | Sin refactor |
| 5.1 | tests/integration/test_client_http.py | contrato OpenAPI | 205/205 | POST cliente inicial 404 antes del registro en 2.1; test OpenAPI nuevo falló por fixture `_IncludedRouter` sin `path`, corregido en test | 1/1 contrato | exactamente cuatro operaciones, handlers async y sin ventas | Sin refactor |
| 5.2 | suite completa, pip y OpenSpec | integración y contrato | 205/205 | No aplica: cierre de regresión | 227/227 en 72,12 s; pip check correcto; OpenSpec strict válido | catálogo, salud y clientes en una sola ejecución; clústeres privados restantes: 0 | Sin refactor |
