# Evidencia TDD C-03

## Línea de base

Antes de editar código existente se ejecutó `python -m pytest -q` con Python del `.venv` del proyecto y PostgreSQL privado (`PG_BIN` apuntando a PostgreSQL 17). Resultado observado: **169 pruebas pasaron en 67,53 s**. No se consultó la configuración personal ni se usó una base ajena.

## Ciclos de implementación

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1 | suite existente | integración | 169/169 | No aplica | 169/169 | No aplica | No aplica |
| 1.2 | tests/integration/test_catalog_isolation.py | integración PG | 169/169 | 2 errores fixture ausente | 2/2 | dos casos: limpieza propia y bloques consecutivos | sin cambios posteriores |
| 2.1 | tests/integration/test_catalog_editoriales.py | HTTP + PostgreSQL | 169/169 | 404 en POST; duplicado IntegrityError | 4/4 | nombres distintos, duplicado, id y campo extra | sin refactor posterior |
| 2.2 | tests/integration/test_catalog_editoriales.py | HTTP + PostgreSQL | 169/169 | GET devolvió 405 | 5/5 | 6/6, conflicto PATCH, nulos y paginación | sin refactor posterior |
| 2.3 | tests/integration/test_catalog_editoriales.py | HTTP + PostgreSQL | 169/169 | ruta devolvió 404 con editorial existente | 7/7 | vacío, padre ausente, paginación, dos libros y dos SQL | sin refactor posterior |
| 3.1 (parcial) | tests/integration/test_catalog_generos.py | HTTP + PostgreSQL | 169/169 | POST 404; libros de género existente 404 | 3/3 | duplicado 409, campos extra, paginación y libros | sin refactor posterior |
| 3.2 | tests/integration/test_catalog_autores.py | HTTP + PostgreSQL | 169/169 | POST 404, detalle 404, PATCH 405, null IntegrityError | 2/2 | dos nombres iguales, null, extra, id inválido e inexistente | sin refactor posterior |
| 3.3 | tests/integration/test_catalog_autores.py | HTTP + PostgreSQL | 169/169 | ruta 404 con autor existente | 3/3 | dos libros y autores, roles, empate, dos SQL, paginación | sin refactor posterior |
| 4.1 | tests/unit/test_catalogo_libro_dto.py y tests/integration/test_catalog_libros.py | DTO y HTTP PG | 169/169 | import faltante; cinco validaciones no rechazadas | 17/17 conjunto | uno/cuatro autores; vacíos, roles, orden y extras | sin refactor posterior |
| 4.2 | tests/unit/test_catalogo_libro_dto.py y tests/integration/test_catalog_libros.py | DTO y HTTP PG | 169/169 | cinco entradas inválidas aceptadas | 17/17 conjunto | 0.01, 1.23, máximo, negativos y exceso | sin refactor posterior |
| 4.3 | tests/integration/test_catalog_libros.py | HTTP + PostgreSQL | 169/169 | POST 404 | 17/17 conjunto | uno y dos autores, género, primera sentencia INSERT | sin refactor posterior |
| 4.4 | tests/integration/test_catalog_libros.py | HTTP + PostgreSQL | 169/169 | FK inválida IntegrityError sin traducir | 17/17 conjunto | FK, ISBN, autor duplicado, ausencia de filas y recuperación | sin refactor posterior |
| 5.1 | tests/integration/test_catalog_libros.py | HTTP + PostgreSQL | 169/169 | GET libros 405 | 1/1 | filtros combinados, caracteres literales, parámetro ligado y límites | sin refactor posterior |
| 5.2 | tests/integration/test_catalog_libros.py | HTTP + PostgreSQL | 169/169 | GET detalle 404 | 1/1 | uno/tres autores, género opcional, empate, 404/422, 2 SQL en ambos | sin refactor posterior |
| 5.3 | tests/integration/test_catalog_libros.py | HTTP + PostgreSQL | 169/169 | PATCH 405; null IntegrityError; precisión aceptada; ISBN IntegrityError | 1/1 | omitir/null, autorías, precio, ISBN y FK, rollback | sin refactor posterior |
| 5.4 | README.md | documentación | 169/169 | No aplica | ejemplos contrastados con rutas probadas | altas, filtro, detalle y PATCH | No aplica |
| 6.1 | tests/integration/test_catalog_routes.py | integración HTTP | 169/169 | RED previos al agregar POST/GET/PATCH de cada módulo | 1/1 | 16 operaciones, handlers async y dos rutas salud | sin refactor posterior |
| 6.2 | suite completa | integración PG y regresión | 169/169 | No aplica | 205/205 | suite previa + escenarios de catálogo | No aplica |

Desviación Strict TDD de 3.1: la traducción de duplicados de género a 409 se escribió junto con el alta antes de ejecutar una prueba RED independiente para ese comportamiento. Luego se probó y pasó. No se inventa un RED retroactivo y la tarea permanece abierta.

Otras desviaciones del orden estricto: en 2.1, `extra='forbid'` se declaró antes de ejecutar RED específico para campos extra; en 2.2, el rechazo de null se añadió antes del RED específico; en 3.2, `extra='forbid'` se declaró antes del RED específico para campos extra. En los tres casos existen RED para las rutas y pruebas posteriores verdes para esos casos, pero no para cada comportamiento antes del código. Las tareas quedan abiertas para reflejar el incumplimiento de proceso; no se fabrican fases RED.

## Verificación integral

En PostgreSQL 17 privado, `python -m pytest -q --tb=short`: **205 pruebas pasaron en 98,01 s**. `python -m pip check`: sin dependencias rotas. `openspec validate catalogo-y-autorias --strict --json`: válido, sin incidencias. Al terminar no quedaron directorios `tmp/pg-foundation-*` de clusters de prueba.
