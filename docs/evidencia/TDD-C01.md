# Evidencia C-01 — foundation-setup

Fecha: 11/11/2026. Baseline inicial: **sin suite previa** (no existían app/, tests/ ni dependencias).

## Entorno observado

- `.venv\Scripts\python.exe --version`: Python 3.12.14.
- `ensurepip` falló inicialmente con PermissionError en TEMP del sandbox; TEMP/TMP del proceso redirigidos a `tmp/foundation-pip`. Segundo intento: Successfully installed pip-25.0.1. No instalación global.
- Descarga inicial PyPI falló por DNS del sandbox; la misma instalación local se ejecutó con escalación acotada autorizada.
- PostgreSQL de pruebas: clúster nuevo con propietario, SCRAM, contraseña aleatoria en memoria, loopback y base libreria_test. Las fixtures nunca leen .env del usuario.

## Ciclos ejecutados

Se agregan resultados reales al completar cada ciclo. Los archivos temporales y logs privados quedan fuera de los entregables.

- Primer RED: `python -m pytest tests/unit/test_config.py -q`: ModuleNotFoundError: app (antes de crear código).
- Primer GREEN: 1 passed; runner necesitó basetemp privado por permisos de TEMP sandbox.
- Triangulación URL: 8 failed, 2 passed por ConfigurationError todavía inexistente; después 10 passed.
- SQL_ECHO RED: 4 failed, 10 passed (atributo ausente y booleano inválido aceptado); GREEN: 14 passed.
- `pip check`: No broken requirements found. Imports runtime y herramientas correctos. pytest 9.2.0.
- Wheels CPython3.12 Windows: asyncpg0.32.0, greenlet3.5.6, pydantic-core2.50.4, httptools0.9.0 descargados.
- Wheels musllinux x86_64: anteriores + uvloop0.23.0 descargados; pydantic-core usa tag1.1, restantes1.2. Primer intento sólo1.2 no encontraba core; añadir1.1 admite wheels compatibles con musl más nuevo. No es un build Alpine.

- Lifespan RED inicial: ModuleNotFoundError app.main; GREEN: 5 passed (3 escenarios de startup/import + 2 guardas PG).
- Infraestructura PG: junctions reales RED 2 failed (tmp redirigido y PGDATA redirigido aceptados), GREEN 2 passed tras guardas. Windows hereda handles de pg_ctl: PIPE se bloqueaba; salida privada a archivo evita espera indefinida, cierre y limpieza tras stop comprobados.
- Motor/fábrica RED: 2 failed, 3 passed (state.engine y módulo database ausentes); GREEN 5 passed.
- Dispose RED: 4 fallos conductuales (normal, conexión, inicialización y fábrica); además 2 errores propios del test por usar atributo privado inexistente de LifespanManager, corregidos usando referencia a app. Estos 2 errores no cuentan como RED conductual.
- Revisión automática de siguiente ejecución no pudo completarse por límite del servicio; no fue rechazo de seguridad. Tras aviso del usuario de límite restaurado, se reanudó GREEN: `python -m pytest tests/unit/test_config.py tests/unit/test_pg_cluster.py tests/integration/test_lifespan.py -q --tb=short`: **27 passed in 31.89s**.

- Creación aditiva RED: 1 failed con UndefinedTableError (tabla registrada aún no creada). GREEN mínimo1 passed30.93s. Triangulación/regresión: `python -m pytest tests/integration/test_database.py tests/integration/test_lifespan.py -q --tb=short`:14 passed40.03s. Se conservó fila y estructura original al añadir columna sólo a metadata; registro de modelos observado antes de create_all; metadata global sin tablas.

- Sesiones RED: ImportError get_session ausente ejecutado antes de implementar dependencia y contratos de duración. GREEN: `python -m pytest tests/integration/test_sessions.py -q --tb=short`:6 passed23.37s. 2 transacciones concurrentes distintas, caché de dependencia dentro de request, cierres normal/error con INSERT revertido, lectura de atributos tras commit sin SQL en dos variantes. expire_on_commit=False ya tenía su RED de fábrica en3.2; sus dos casos de atributos son regresión adicional y no se atribuye un RED aislado inexistente.

- Live RED: 2 failed (404 en ambos estados PG); GREEN2 passed24.97s. Instrumentación SQL y fábrica que falla si se invoca verificaron cero consultas/cero sesiones con DB accesible y caída real posterior al startup; fixture recuperó y retiró sólo PG privado.

- Ready RED:2 failed(404),2 passed(live); GREEN4 passed26.37s. Una/tres peticiones produjeron exactamente SELECT1 nuevo y cierre de sesión en cada caso.

- Revisión detectó error de conexión por base inexistente sin traducir. Reabierta3.3; RED específico1 failed(InvalidCatalogNameError),11 deselected. Incluida sólo esa excepción de conexión; GREEN regresión lifespan12 passed31.63s. No se agregó captura genérica de PostgresError/ProgrammingError.

- 503 RED inicial3 failed5 passed; ampliado a adquisición previa al handler:5 failed6 passed34.16s. GREEN de comportamiento17 passed con2 errores de teardown del test por undo repetido sobre State; restauración del doble cambiada a try/finally. GREEN final health+sesiones17 passed35.27s sin errores. Fallo de fábrica, entrada de contexto, conexión y consulta responden503 exacto; ProgrammingError/RuntimeError conservados; prueba real200→paradaPG→503/live200→reinicioPG→200 y pool sin conexiones prestadas.

- Revisión de desconexión durante execute: RED DBAPIError(connection_invalidated=True)1 failed1 passed11 deselected25.24s; caso no invalidado permaneció sin503. Clasificador compartido distingue desconexión de ProgrammingError/IntegrityError/DataError. GREEN health+lifespan25 passed50.23s; caída/recuperación real conservada.
- Servidor Uvicorn0.54.0 CPython3.12.14 Windows verificado por CLI --version. `test_server.py` inicia el objeto documentado app.main:app en Uvicorn real, loopback/puerto libre, HTTP real live/ready/docs; should_exit y engine_disposed comprueban apagado:1 passed24.26s. Usa Config equivalente al comando README, puerto propio para preservar otros servicios.
- README, env.example y .gitignore revisados: marcadores ficticios, entorno priorizado, SQL_ECHO, distinción motor/fábrica/sesión, no commit automático, create_all aditivo, salud exacta y límites C02/C07/C08. Comandos de instalación desde requirements-dev comprobados sobre .venv preparada (sin descargas adicionales); exclusiones privadas presentes.
- Todas las extensiones transitivas detectadas en Windows (.pyd) tienen distribución instalable para musl: MarkupSafe3.0.4, PyYAML6.0.3, SQLAlchemy2.0.57, asyncpg0.32.0, charset-normalizer3.5.2, fastar0.12.0, greenlet3.5.6, httptools0.9.0, protobuf7.36.2 (wheel universal), pydantic-core2.50.4, rignore0.8.1, watchfiles1.3.0, websockets17.4; además uvloop0.23.0 para Linux. Descarga pip --only-binary --no-deps --platform musllinux_1_2_x86_64 --platform musllinux_1_1_x86_64 --implementation cp --python-version312 --abi cp312 exit0. Windows tiene los wheels instalados y las cuatro descargas críticas registradas arriba. Esto no demuestra build ni ejecución Alpine.

## Verificación final

`python -m pytest -q --tb=short` (con `.venv` Python3.12.14): **51 passed in 42.30s**. PostgreSQL17 privado, sin SQLite. Incluye14 casos de configuración,2 guardas con junctions reales,3 creación aditiva,12 lifespan,6 sesiones,13 health y1 servidor HTTP Uvicorn real.

`python -m pip check`: **No broken requirements found**. `python -m compileall -q app tests`: exit0. Revisión de `app/`: sin `time.sleep`, `requests`, DB síncrona, `drop_all`, SQLite, URL fallback ni tablas ficticias; los siete módulos tienen models/schemas/service/router. El refactor final sólo distribuyó imports/llamada del motor y añadió docstring de lifespan; la suite51 quedó verde tras ese paso.

### TDD Cycle Evidence

Los números GREEN corresponden a ejecuciones descritas arriba; «regresión final51» designa la suite conjunta. N/A indica entorno/documentación/verificación directa, que no requiere pruebas artificiales. El primer baseline fue «sin suite previa»; después se ejecutaron las suites relevantes antes de ampliar comportamiento. No se presentan errores de fixtures/tests como RED conductual.

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
|1.1|N/A|Entorno|Sin entorno anterior|N/A|Python3.12.14/pip25.0.1|venv y pip operativos|N/A|
|1.2|requirements*.txt|Dependencias|Sin dependencias previas|N/A|pip check/imports/runner|Windows/musl; todas extensiones|N/A|
|1.3|tests/unit/test_config.py|Unit|Sin suite previa|app inexistente|1; luego14|Modo strict/loop función|Regresión final51|
|1.4|tests/unit/test_pg_cluster.py|Infraestructura|Sin suite específica inicial|2 junctions aceptados|2|tmp y PGDATA redirigidos; PGSQL real|Regresión final51|
|1.5|README.md/.gitignore|Documentación|N/A|N/A|Comandos revisados/ejecutados|Privados excluidos|N/A|
|2.1|tests/unit/test_config.py|Unit|Sin código previo|Import ausente; luego8 inválidas|10|Entorno/.env/falta/vacío/formato/controlador|14 verdes tras ajuste|
|2.2|tests/unit/test_config.py; test_lifespan.py|Unit/integración|10 pasan|4 fallan atributo/validación|14; motor en lifespan|Omitido/false/TRUE/inválido|Regresión final51|
|2.3|env.example/README.md|Documentación|N/A|N/A|Revisión directa|Sin credenciales, prioridad documentada|N/A|
|3.1|tests/integration/test_lifespan.py|Integración|Config14 pasan|app.main inexistente|3 escenarios; conjunto5|Import sin red/PG accesible/sin URL|Regresión final51|
|3.2|tests/integration/test_lifespan.py|Integración|Lifespan3+guardas2 pasan|Motor/fábrica ausentes; módulo DB ausente|5|Dos apps/refused/metadata vacía|Regresión final51|
|3.3|tests/integration/test_lifespan.py|Integración/límite DB|Lifespan5 pasan|4 dispose;1 base inexistente|12|Normal/conexión/inicialización/fábrica; secreto oculto|Regresión final51|
|3.4|tests/integration/test_database.py|Integración PostgreSQL|Conjunto27 pasan|UndefinedTableError|1; luego conjunto14|Crear/conservar fila y estructura/vacía/orden registro|Regresión final51|
|3.5|README.md; test_server.py|Documentación/servidor|Lifespan/create_all verdes|N/A verificación|Uvicorn1|HTTP real y dispose al apagar|N/A|
|4.1|tests/integration/test_sessions.py|Integración PostgreSQL|Lifespan/create_all14 pasan|get_session inexistente|6|Concurrencia/transacciones distintas/caché request|Regresión final51|
|4.2|tests/integration/test_sessions.py|Integración PostgreSQL|Mismo ciclo cohesivo4.1|Compartido: get_session ausente; expire_on_commit tuvo RED3.2|6|Normal/error sin commit;2 atributos tras commit|Regresión final51|
|4.3|README.md|Documentación|Sesiones6 verdes|N/A|Recorrido y ownership revisados|Sin commit automático/sin UoW|N/A|
|5.1|tests/integration/test_health.py|Integración PostgreSQL|Sesiones6 pasan|2 respuestas404|2|PG accesible/caída real;0SQL/0sesiones|Regresión final51|
|5.2|tests/integration/test_health.py|Integración PostgreSQL|Live2 pasan|2 respuestas404|4|1/3 peticiones; SELECT1 por cada una; cierre|Regresión final51|
|5.3|tests/integration/test_health.py|Integración/límite DB|Health4 pasan|5 casos503 ausente; luegoDBAPI invalidada1|17 health/sesiones;25 health/lifespan|Factory/entrada/conexión/consulta/recuperación real; errores programación preservados|Regresión final51|
|5.4|README.md|Documentación|Contratos health verdes|N/A|Respuestas contra pruebas|Startup/live/ready/503/recuperación|N/A|
|6.1|tests/; app/|Regresión/inspección|Suites parciales verdes|N/A|51 pasan; imports/compile/pip check|Estructura+config+DB+HTTP|51 tras refactor legibilidad|
|6.2|docs/evidencia/TDD-C01.md|Evidencia|Resultados reales anteriores|N/A|23 filas y escenarios mapeados|Límites y comandos sanitizados|N/A|
|6.3|tests/pg_cluster.py; auditoría final|Teardown|Guardas2 verdes|N/A cierre verificado|pg_ctl stop -w, PID ausente y directorio propio retirado|Cierres normal/excepción/caída/recuperación|N/A|

## Trazabilidad de escenarios

|Spec / requirement|Escenarios cubiertos|Evidencia|
|---|---|---|
|application-foundation / configuración|Entorno prioritario, sólo.env, ausente/vacía/inválida, SQL_ECHO tres variantes y texto inválido|test_config.py14; test_lifespan.py eco false/TRUE|
|application-foundation / arranque|PG accesible, conexión rechazada, import independiente|test_lifespan.py; HTTP servido sólo tras entrar al lifespan; import en subproceso con socket.connect prohibido|
|application-foundation / creación aditiva|Tabla ausente, tabla/fila/estructura conservada, registro vacío|test_database.py3; metadata auxiliar local y SQLModel global vacío|
|application-foundation / sesiones|Concurrentes distintas, dependencia reutilizada, cierre normal/error sin commit, atributos después de commit|test_sessions.py6; txid_current distintos, INSERT revertido y ceroSQL al leer atributos|
|application-foundation / recursos|Apagado, fallo parcial, instancias independientes|test_lifespan.py; evento engine_disposed y motores/fábricas distintos|
|health-monitoring / live|DB disponible y caída posterior a startup|test_health.py dos estados reales con fábrica prohibida y observador SQL|
|health-monitoring / ready|Disponible, adquisición fallida, consulta fallida, recuperación|test_health.py13; factory/entrada, excepciones concretas, DBAPI invalidada, PG stop/start real|

## Límites y próximo alcance

No se ejecutó build Alpine/Docker ni despliegue VPS: corresponden a C-07/C-08. La comprobación de wheels no sustituye ese build. La suite actual necesita binarios PostgreSQL17 y permisos locales para loopback y junctions; la API admite PostgreSQL16+. En este sandbox hubo que ejecutar las pruebas async con permiso de red local, sin cambiar servicios globales.

Los módulos de negocio permanecen sin entidades/CRUD. C-02 incorporará las nueve tablas; seed, .http y evidencias académicas C/D se realizan en sus changes. El change queda implementado, sin archive automático, commit, push ni publicación.

Auditoría final:23 filas de evidencia y7 módulos completos comprobados;0 directorios `tmp/pg-foundation-*` pendientes. Cada teardown hizo pg_ctl stop -w, verificó ausencia de postmaster.pid y retiró sólo el directorio con marcador propio; no quedan contraseñas temporales de esos clústeres. Las únicas URL literales de los entregables de ejecución/documentación son marcadores USUARIO/CLAVE/HOST/BASE. `openspec validate foundation-setup --strict --json`: valid=true, issues=[], exit0.
