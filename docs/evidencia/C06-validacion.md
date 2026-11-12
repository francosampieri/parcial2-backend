# C-06 — validación integral y datos

Fecha de ejecución: 2026-11-12. Entorno: Python 3.12, PostgreSQL 17.10 privado de la suite, loopback, base efímera; sin conexión a la VPS ni a `.env` personal.

## Seed y TDD

`tests/integration/test_demo_seed.py` verificó creación de los cuatro libros, IDs devueltos, segunda ejecución sin duplicados, rechazo de datos discrepantes y autor ambiguo. El caso de ambigüedad usa una transacción anidada y comprueba que no queda una editorial insertada a medias. RED inicial: 2 fallos por `ModuleNotFoundError: app.demo_seed`; GREEN: 2/2. Para el libro con dos autores, RED: 1 fallo (había uno); GREEN: 3/3. Después se agregaron dos casos dirigidos de discrepancia/ambigüedad; su comportamiento ya estaba implementado, por lo que no se atribuye un RED independiente a esos casos.

| Tarea | Prueba | Capa | Safety net | RED | GREEN | Triangulación | Refactor |
|---|---|---|---|---|---|---|---|
| 1.1–1.2 | `test_demo_seed.py` | Integración PG | No se modificó código existente | 2 fallos: módulo ausente | 2/2 | 3/3, libro multi autor | Registro central de modelos, 3/3 |
| 1.3 | `test_demo_seed.py` | Integración PG | 3/3 | No independiente | 5/5 con caso integral | Discrepancia y ambigüedad | Error CLI claro; suite 274/274 |
| 3.1–3.2 | `test_c06_integral.py` | Integración PG + ASGI | C05 269/269 conocido | No independiente: verifica flujo ya implementado | 1/1 | 1/2 cardinalidades | Limpieza propia tras primera corrida contaminante |

La primera corrida de la suite completa encontró 80 fallos porque la prueba integral dejó filas persistidas y varias pruebas previas usan IDs fijos. Se agregó limpieza **sólo de las filas creadas por esa prueba**. Segunda corrida completa: **274 passed in 89.80s**. Este es un problema de aislamiento del test, no un fallo de la API.

## Venta, precio histórico y reinicio

La prueba `tests/integration/test_c06_integral.py` cargó seed y creó una venta de dos renglones: 2 × 25.000,00 + 1 × 27.000,00 = **77.000,00**. Luego modificó el precio del primer libro a 30.000,00. `GET /ventas/{id}` conservó el total 77.000,00 y el precio unitario histórico 25.000,00. Se cerró la primera instancia de FastAPI y se inició otra contra la **misma base PostgreSQL**; la venta seguía disponible sin reejecutar el seed. La API reinició, no el servidor PostgreSQL, que es el mecanismo pertinente para verificar persistencia de aplicación.

## Conteo SQL C-07

Se registraron eventos `before_cursor_execute` del motor SQLAlchemy solamente alrededor de cada `GET` de detalle; seed, POST, PATCH, startup y cleanup quedaron fuera de esa ventana. Se contaron sentencias `SELECT` emitidas por cada petición, incluida la serialización de la respuesta. Resultado observado:

| Detalle | Cardinalidad | SELECT |
|---|---:|---:|
| Libro | 1 autor | 2 |
| Libro | 2 autores | 2 |
| Venta | 1 renglón | 2 |
| Venta | 2 renglones | 2 |

Salida sanitizada del caso focalizado: `C06_EVIDENCE book_selects=2/2 sale_selects=2/2 total=77000.00 historical_price=25000.00`; **5 passed in 25.40s**. No se guardaron URLs, contraseñas ni datos personales reales. Reproducción en PowerShell desde la raíz del proyecto:

```powershell
$env:PG_BIN = Join-Path $env:ProgramFiles 'PostgreSQL\17\bin'
.\.venv\Scripts\python.exe -m pytest tests/integration/test_demo_seed.py tests/integration/test_c06_integral.py -q -s
```

## Recorrido HTTP

`test/C-01-a-C-08.http` contiene las 26 rutas distintas `[OP 01]` a `[OP 26]` y los errores C-01 a C-08. Sus variables iniciales se sustituyen por los IDs reales que devuelve el seed; los POST del recorrido capturan sus IDs con REST Client. `python -m test.verify_examples` ejecutó **las 39 peticiones exactas del archivo** contra un PostgreSQL 17.10 privado, capturando IDs dinámicamente y comprobando cada código esperado: `HTTP_EXAMPLES 39 peticiones verificadas, 26 operaciones, C-01 a C-08 OK`. El cliente REST interactivo queda disponible para la demostración manual; no se afirma que la extensión REST Client haya sido ejecutada en esta sesión.
