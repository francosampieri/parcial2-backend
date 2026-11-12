# Evidencia TDD C-05

## Línea de base

Antes de modificar archivos se ejecutó `PG_BIN=/usr/bin .venv/bin/python -m pytest -q` con Python 3.14.7 del `.venv` del proyecto y PostgreSQL 18.6 privado. Resultado observado: **227 pruebas pasaron en 5,75 s**. No se consultó el `.env` personal ni se usó una base ajena. No quedaron directorios `tmp/pg-foundation-*`.

## Ciclos de implementación

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1 | suite existente | Integración | — | No aplica | 227/227 en 5,75 s | No aplica | No aplica |
| 1.2 | test_sale_isolation.py | Integración PG | 227/227 | fixture `sale_seed` ausente: 2 errors | 2/2 | dos grupos con IDs distintos, fila ajena preservada | sin refactor |
| 1.3 | test_venta_dto.py | Unitaria | 227/227 | ImportError: 16 fallos | 16/16 | uno/varios renglones, vacío, duplicado, cantidad 0/-1, campos calculados y desconocidos | sin refactor |
| 2.1 | test_sale_http.py | HTTP + PostgreSQL | 227/227 | POST 404: 2 fallos | 2/2 | dos renglones y un renglón con importe mínimo | sin refactor |
| 2.2 | test_sale_http.py | HTTP + PostgreSQL | 227/227 | POST 404 (RED compartido con 2.1) | 2/2 | 25000×2 + 27000×1 = 77000.00 y 0.10×3 = 0.30, importes como cadena y fecha con offset | sin refactor |
| 2.3 | test_sale_atomicity.py | HTTP + PostgreSQL | 227/227 | comprobaciones desactivadas temporalmente: 3 fallos (500/KeyError en vez de 409) | 9/9 | cliente ausente, libro ausente, recuperación posterior y 6 contratos inválidos sin filas | sin refactor |
| 2.4 | test_sale_atomicity.py | HTTP + PostgreSQL | 227/227 | FK borrada entre lectura y confirmación: IntegrityError propagado, 1 fallo | 10/10 | rollback sin filas y venta válida posterior | extracción de `_cargar_libros`, 10 verdes |
| 2.5 | test_sale_http.py | HTTP + PostgreSQL | 227/227 | `GET /ventas/{id}` 404: 1 fallo | 3/3 | PATCH del libro después de vender; precio y subtotal originales | sin refactor |
| 2.6 | README.md | Documentación | 227/227 | No aplica | Contrato y ejemplo cotejados con pruebas verdes | campos calculados, 409 y precio histórico | No aplica |
| 3.1 | test_sale_reads.py | HTTP + PostgreSQL | 227/227 | listado y validaciones 404: 6 fallos, 1 verde | 7/7 conjunto | resumen con cuatro campos, orden por ID, `limit=1`, offset alto vacío y tres paginaciones inválidas | sin refactor |
| 3.2 | test_sale_reads.py | HTTP + PostgreSQL | 227/227 | detalle ya disponible; errores 404/422 en RED del listado | 7/7 conjunto | detalle con dos renglones, títulos y subtotales, ID inexistente y no entero | sin refactor |
| 3.3 | test_sale_reads.py | HTTP + PostgreSQL | 227/227 | ruta 404 antes de registrarla | 7/7 conjunto | dos clientes con ventas, cliente sin ventas, 404, 422 y límite inválido | sin refactor |
| 3.4 | test_sale_reads.py | HTTP + PostgreSQL | 227/227 | conteo no disponible sin rutas | listado 1 SQL; ventas por cliente 2 SQL; detalle igual con 1 y 3 renglones (≤2) | dos tamaños de detalle y tres lecturas distintas | sin refactor |
| 3.5 | README.md | Documentación | 227/227 | No aplica | Rutas, resumen y detalle cotejados con pruebas verdes | lista vacía, 404/422 y paginación | No aplica |
| 4.1 | test_venta_aviso.py; test_sale_aviso.py | Unitaria + HTTP | 227/227 | ImportError en unitaria; spy no llamado y log ausente en integración: 3 fallos | 3/3 | aviso válido con espera ≥0,5 s; alta rechazada no agenda; alta válida agenda una vez | sin refactor |
| 4.2 | test_sale_aviso.py | HTTP real con uvicorn | 227/227 | Log de comprobante ausente con timeout | 201 antes de 0,5 s, health atendido y log posterior | orden respuesta→aviso y concurrencia durante la espera | sin refactor |
| 4.3 | README.md | Documentación | 227/227 | No aplica | Diferencia tarea/cola y ausencia de sesión cotejadas con prueba real | orden y concurrencia | No aplica |
| 5.1 | test_client_http.py; test_sale_http.py | Contrato OpenAPI | 227/227 | C-04 falló al detectar la quinta ruta de clientes | 2/2 | exactamente cuatro operaciones de ventas, todas async, sin PATCH ni renglones sueltos | sin refactor |
| 5.2 | suite completa, pip y OpenSpec | Integración y contrato | 227/227 | No aplica: cierre de regresión | 269/269 | catálogo, clientes, salud y ventas en una sola ejecución | No aplica |
| 5.3 | CHANGES.md | Documentación | 269/269 | No aplica | Estado marcado tras verificación | No aplica | No aplica |

## Resultado integral

`PG_BIN=/usr/bin .venv/bin/python -m pytest -q`: **269 passed in 14.14 s** (durante el cierre se repitió la ejecución con el mismo resultado). `pip check`: sin dependencias rotas. `openspec validate ventas-y-comprobantes --strict`: válido. Sin directorios `tmp/pg-foundation-*` al terminar.

## Notas de fidelidad TDD

- Las tareas 2.1 y 2.2 compartieron el mismo RED (POST inexistente); la copia de precios y el cálculo se implementaron junto con el alta mínima.
- La comprobación de referencias de 2.3 se había escrito junto con 2.1. Para verificar que las pruebas detectan su ausencia, se desactivó temporalmente y se ejecutó el RED (3 fallos por 500/KeyError); luego se restauró y quedaron 9 verdes.
- El detalle de 3.2 se implementó antes de 2.5 porque la conservación del precio histórico se verifica por `GET /ventas/{id}`; el RED de 2.5 fue el 404 de esa ruta.
- Las tareas documentales no tienen ciclo artificial; sus afirmaciones se cotejaron contra las pruebas verdes.

## Archivo

Change archivado el 12/11/2026 en `openspec/changes/archive/2026-11-12-ventas-y-comprobantes/`. Se creó la spec principal `ventas-http` (6 requisitos) y se actualizó la cláusula de `clientes-http` que reservaba `GET /clientes/{id}/ventas`. `openspec validate --specs`: 6/6 specs válidas.

