# Evidencia TDD C-02

## Baseline

Antes de editar archivos existentes: `PG_BIN=C:\Program Files\PostgreSQL\17\bin .venv\Scripts\python.exe -m pytest -q` → **51 passed in 57.39s**. PostgreSQL privado administrado por las fixtures del proyecto.

## Aislamiento (1.2)

RED: la fixture `domain_session` no existia (2 errores). GREEN: dos casos parametrizados pasaron con una transaccion por prueba. Triangulacion: una insercion de otra conexion permanece intacta tras rollback de la sesion; 3 pruebas pasaron. Refactor: se evita rollback repetido si ya se cerro la transaccion y se volvieron a ejecutar las 3 pruebas sin advertencias.

## Avance de modelos (tareas aun pendientes)

- Tablas y columnas: RED 9 fallos; GREEN 10 pruebas.
- Precision y fecha: RED 3 importes sin precision; GREEN 4 pruebas.
- CHECK: RED 7 valores invalidos aceptados; GREEN 7 pruebas.
- UNIQUE y PK compuesta: RED 5 duplicados aceptados, una PK ya protegida; GREEN 6 pruebas.
- FK: RED 8 referencias invalidas aceptadas; GREEN 8 pruebas.
- Indices FK: RED 6 coberturas ausentes, otras 2 cubiertas; GREEN 8 pruebas.
- Relaciones: RED 9 mapeos ausentes; GREEN 9 pruebas de mapeo; triangulacion navegacion real catalogo 2 pruebas.
- Prueba de C-01: fallo esperado de metadata vacia reemplazado por nueve tablas; GREEN 3 pruebas de database.
- Perfil escalar (4.2): RED de mapeo inexistente; GREEN y triangulacion en PostgreSQL con y sin perfil (2 pruebas), navegacion inversa sin SQL adicional. Segundo perfil rechazado en test de unicidad.
- Indices (3.4): RED 6 ausentes y 2 coberturas ya existentes; GREEN 8 coberturas, triangulacion 2 comprobaciones sin indices duplicados; 10 pruebas verdes.
- Importes/fecha (2.2): RED precision ausente en los 3 campos; GREEN tipos exactos. Triangulacion en PG con 0.01, 0.10, maximos y exceso (SQLSTATE 22003), UTC y offset -03:00; 9 pruebas. Una suposicion inicial del test esperaba DataError pero asyncpg expone DBAPIError, corregida para comprobar SQLSTATE real. Refactor DateTime(timezone=True) explicito y 9 verdes nuevamente.
- CHECK (3.2): RED 7 reglas ausentes; GREEN 7. Triangulacion agrega cuatro roles admitidos y valores cero/negativos con escrituras SQL reales: 15 pruebas verdes. Los limites validos 0/1/0.01 se cubren en estas pruebas y en `test_decimales_exactos_y_limites`.
- FK (3.3): RED 8 referencias invalidas aceptadas; GREEN 8 fallos de integridad esperados. Cada caso inserta previamente una referencia valida; triangulacion genero NULL en `test_ids_generados_y_genero_ausente`. No se agregaron cascadas.
- Unicidad (3.1): RED 5 campos sin UNIQUE; GREEN 6 duplicados rechazados incluyendo PK compuesta. Triangulacion: valores distintos para las cinco restricciones y tres parejas libro/autor validas, con orden compartido; 7 pruebas verdes.
- Transacciones (5.1, 5.2): las restricciones habian pasado RED con datos invalidos aceptados. Dos pruebas PG ejercitan alta libro/autoria y venta/renglon: error IntegrityError, rollback, comprobacion desde otra conexion sin filas parciales, reutilizacion de la misma sesion con alta valida y commit; 2 verdes. Solo se eliminan filas creadas por cada prueba en la base privada.
- Registro y arranque (6.1): la prueba de C-01 fallo al esperar metadata vacia; se actualizo a nueve tablas conservando verificacion orden registro/create_all. Triangulacion: dos arranques conservan fila de cliente y tabla ajena con estructura y datos; suite test_database 4/4 verdes, sin modificar columnas existentes.
- Esquema (2.1): RED 9 tablas/columnas incompletas; GREEN 10 pruebas iniciales. Triangulacion: insercion y lectura de las nueve entidades, IDs generados y genero NULL (11 pruebas de esquema), y 34 columnas obligatorias rechazando NULL en PostgreSQL. PK compuesta y registro con orden cubiertos por unicidad y test_database.
- Relaciones catalogo (4.1): RED mapeos ausentes; GREEN mapeos y triangulacion PG con 1/2 autores, roles autor/traductor, orden y genero presente/ausente. Cuatro casos de navegacion inversa con todas las rutas precargadas y cero SQL al recorrer; refactor de comparacion sin asumir orden y prueba verde.
- Relaciones ventas (4.3): RED mapeos ausentes, GREEN relaciones. Triangulacion PG con una/dos ventas y uno/dos renglones, relaciones inversas precargadas, cantidades y precios, sin SQL adicional: 2 casos verdes tras ampliacion.
- Documentacion (2.3, 3.5, 4.4, 6.2): README cotejado con tablas y columnas, tipos, ocho FK e indices, relaciones y limites de create_all. Se aclaro diferencia entre flush y commit. Enlaces de tests/evidencia existentes; documentacion no requiere test artificial.

## Resultado integral

`PG_BIN` dirigido a PostgreSQL 17 privado y `python -m pytest -q`: **169 passed in 68.94s**, sin advertencias. `openspec validate core-domain-models --strict --json`: valido, sin incidencias. `pip check`: sin dependencias rotas. Sin directorios `tmp/pg-foundation-*` al terminar.

## Tabla de evidencia TDD

La baseline 51/51 corresponde al comienzo de C-02. Una prueba de metadata de C-01 tenia una expectativa temporal vacia y fue actualizada despues de comprobar su fallo por la presencia de modelos. Las pruebas de transacciones se escribieron despues de las restricciones cuyo RED ya se habia ejecutado; no se afirma un RED independiente para ellas. Las tareas documentales no tienen ciclo artificial.

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1 | suite C-01 | Integracion | 51/51 | No aplica | 51/51 | No aplica | No aplica |
| 1.2 | test_domain_isolation.py | Integracion | 51/51 | fixture ausente | 2 casos | 3 casos, rollback ajeno | rollback activo, 3 verdes |
| 2.1 | test_domain_schema.py; test_domain_constraints.py; test_database.py | Integracion | 51/51 | 9 tablas/columnas incompletas | esquema 10 verdes | insercion 9 entidades, 34 NULL, IDs, genero NULL | sin refactor productivo |
| 2.2 | test_domain_schema.py | Integracion | 51/51 | 3 precisiones ausentes | 4 tipos | 9 casos min/max/overflow/offset | fecha explicita, 9 verdes |
| 2.3 | README.md | Documentacion | 51/51 | No aplica | revision | cotejo tablas/tipos | aclaracion flush/commit |
| 3.1 | test_domain_constraints.py | Integracion | 51/51 | 5 duplicados aceptados | 6 rechazos | 7 casos y orden compartido | sin refactor productivo |
| 3.2 | test_domain_constraints.py | Integracion | 51/51 | 7 valores invalidos aceptados | 7 rechazos | 15 bordes/roles | sin refactor productivo |
| 3.3 | test_domain_constraints.py; test_domain_schema.py | Integracion | 51/51 | 8 referencias invalidas aceptadas | 8 rechazos | validas y genero NULL | sin refactor productivo |
| 3.4 | test_domain_schema.py | Integracion | 51/51 | 6 indices ausentes | 8 coberturas | 10 casos sin duplicacion | sin refactor productivo |
| 3.5 | README.md | Documentacion | 51/51 | No aplica | revision | matriz 8 FK | No aplica |
| 4.1 | test_domain_relationships.py | Integracion | 51/51 | relaciones ausentes | mapeos | 4 recorridos y sin SQL | orden no supuesto, verde |
| 4.2 | test_domain_relationships.py; test_domain_constraints.py | Integracion | 51/51 | relaciones ausentes | mapeo | perfil presente/ausente, duplicado rechazado | sin refactor productivo |
| 4.3 | test_domain_relationships.py | Integracion | 51/51 | relaciones ausentes | mapeos | 2 recorridos venta/renglones | ampliacion ventas multiples verde |
| 4.4 | README.md | Documentacion | 51/51 | No aplica | revision | ejemplos y precarga | No aplica |
| 5.1 | test_domain_transactions.py | Integracion | 51/51 | RED previo de CHECK/FK, sin RED transaccional independiente | rollback y reuso | caso valido e invalido, consulta independiente | sin refactor productivo |
| 5.2 | test_domain_transactions.py | Integracion | 51/51 | RED previo de CHECK/FK, sin RED transaccional independiente | rollback y reuso | caso valido e invalido, consulta independiente | sin refactor productivo |
| 6.1 | test_database.py | Integracion | 51/51 | expectativa metadata vacia obsoleta falla | registro completo y orden | 2 arranques, tabla ajena, 4 verdes | sin refactor productivo |
| 6.2 | README.md | Documentacion | 51/51 | No aplica | revision | cotejo arranque/pruebas | No aplica |
| 7.1 | suite completa | Integracion | 51/51 | No aplica | 169/169 | regresion completa | No aplica |

## Desviacion respecto de Strict TDD

Las tareas 5.1 y 5.2 se verificaron con pruebas transaccionales reales escritas despues de que ya existian las restricciones y el manejo de sesiones. Aunque previamente se ejecutaron RED para las restricciones, no se ejecuto un RED independiente de esas pruebas transaccionales antes de disponer del comportamiento; por tanto, estas tareas no siguieron integramente el ciclo TDD exigido. La adaptacion de la prueba de metadata de C-01 tambien se hizo despues de agregar modelos, observando que la expectativa anterior fallaba; no se escribio primero una prueba nueva del contrato futuro. No se presenta un RED retroactivo. La verificacion funcional real si paso.
