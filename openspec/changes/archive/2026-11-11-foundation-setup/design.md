# Design

## Context

Ver `proposal.md` para la motivación; `AGENTS.md`, C-01 de `CHANGES.md` y KB 02/06/07/08/09/10 delimitan el alcance. No existen `app/`, pruebas automatizadas ni dependencias de API instaladas en el Python por defecto. El inventario de specs principales está vacío. La propuesta requiere diseño porque configuración, sesiones y lifecycle atraviesan toda la aplicación.

Inspección de lectura del 11/11/2026:

| Recurso | Observación | Consecuencia para apply |
|---|---|---|
| Python por defecto / `py` | 3.14.7; el launcher sólo enumera 3.14 | Cumple el mínimo, pero conviene probar con la misma rama 3.12 de la imagen futura |
| Python bundled de herramientas | 3.12.14 ejecutable y módulo `venv` disponible | Usarlo para crear `.venv` local; no fijar su ruta en la aplicación ni exigir Codex a otros integrantes |
| PostgreSQL | Binarios `postgres`, `initdb` y `pg_ctl` 17.10 en `C:\Program Files\PostgreSQL\17\bin` | Reutilizar binarios para un clúster privado; 17 cumple el mínimo 16 |
| Servidor local | `pg_isready` a `127.0.0.1:5432`: sin respuesta; no se observaron procesos postgres | No prueba ausencia de otras instalaciones/puertos; no usar ni modificar el directorio `data` de esa instalación |
| Servicios Windows | Inspección SCM no permitida | No afirmar estado de servicios ni pedir elevar privilegios para este desarrollo |
| Docker | CLI 29.8.2, contexto desktop-linux; daemon inaccesible | No es prerrequisito para API/pruebas con PostgreSQL privado; Dockerfile/build pertenecen a C-07 |
| Herramientas | `uv`, `psql`, `pg_ctl` fuera de PATH; paquetes de API/pytest ausentes del Python por defecto | Usar ejecutables explícitos para este equipo y registrar dependencias en el proyecto |

Estas observaciones describen esta máquina. No se instaló nada, no se ejecutó `initdb`, no se inició PostgreSQL/Docker y no se consultaron credenciales ni bases ajenas.

## Goals / Non-Goals

**Goals:**
- Crear una aplicación que pueda importarse sin efectos de red, inicializarse antes de servir y liberar recursos también si falla a mitad del startup.
- Mantener motor compartido por instancia y sesiones independientes por petición; preparar contratos estables para C-02 en adelante.
- Hacer reproducible TDD con PostgreSQL aislado y explicar qué demuestra cada prueba.

**Non-Goals:**
- No crear las nueve tablas ni endpoints de negocio, ni extraer una capa de repositorios/UoW.
- No producir migraciones, seed, reset de datos, contenedor de aplicación ni publicación. La comprobación final Alpine/Docker se realiza en C-07.
- No inventar DTO de entrada para salud. `extra='forbid'` se aplicará a todos los DTO de entrada cuando se incorporen en los changes de dominio.

## Decisions

### 1. Dependencias y runtime reproducibles

Crear `.venv` con Python 3.12 disponible en la máquina; fuera de ella documentar un intérprete Python 3.12+ sin rutas personales. Mantener sintaxis compatible con 3.12. Separar `requirements.txt` de ejecución y `requirements-dev.txt` que lo incluya y añada `pytest`, `pytest-asyncio`, `httpx` y `asgi-lifespan`. Es el conjunto mínimo elegido para TDD async y pruebas del lifespan; no añadir plugins de cobertura, contenedores o generadores por costumbre.

Resolver durante la preparación de apply versiones publicadas compatibles: `fastapi[standard]>=0.111`, `sqlmodel>=0.0.24`, `SQLAlchemy[asyncio]>=2.0`, `asyncpg>=0.30`, `python-dotenv>=1.0`. Respetar las restricciones transitivas declaradas por SQLModel y FastAPI; no forzar SQLAlchemy 2.1 si el SQLModel resuelto exige `<2.1`. Registrar versiones exactas realmente resueltas y comprobar `pip check`, imports y runner antes del código productivo. El extra `SQLAlchemy[asyncio]` explicita el soporte greenlet requerido por su integración async.

Antes de fijar esas versiones, verificar disponibilidad de distribuciones binarias para Windows CPython 3.12 y Linux musllinux CPython 3.12 de las extensiones transitivas aplicables (`asyncpg`, `greenlet`, `pydantic-core`, `uvloop`/`httptools` cuando correspondan). Usar metadatos oficiales y resolución de pip para el objetivo; no inferir compatibilidad Alpine de una instalación Windows exitosa ni añadir compiladores por defecto. Esta comprobación de dependencias no reemplaza el build C-07. Si no hay una combinación compatible con los mínimos y sin compiladores, detener esa tarea con el conflicto concreto antes de modificar arquitectura.

**Alternativas:** Python 3.14 local también satisface el mínimo, pero aumenta diferencias con la base obligatoria; instalar otro Python no aporta valor si 3.12 funciona. Una lista de pins inventados no demostraría compatibilidad. Las publicaciones de [SQLModel](https://pypi.org/project/sqlmodel/), [asyncpg](https://pypi.org/project/asyncpg/) y [greenlet](https://pypi.org/project/greenlet/) permiten contrastar requisitos y wheels en el momento de resolver.

### 2. Clúster PostgreSQL privado sin Docker ni servicios globales

En apply preparar un directorio nuevo bajo `tmp/pg-foundation-<identificador>/`, con PGDATA, logs y marcador de propiedad propios; verificar su ruta absoluta dentro del workspace antes de crear o limpiar. Usar `initdb` de PostgreSQL 17 ya instalado, codificación UTF-8 y autenticación local `scram-sha-256`, con contraseña efímera generada, suministrada por archivo temporal de contraseña y eliminada después de inicializar. No mostrar ni versionar la contraseña. Usar sólo `127.0.0.1`, un puerto libre verificado justo antes de iniciar (5433 como candidato, cambiar sólo el puerto si está ocupado), y `pg_ctl` con logs privados. No registrar servicio Windows ni tocar `C:\Program Files\PostgreSQL\17\data`.

Crear dentro de ese clúster únicamente la base `libreria_test`; construir la URL en memoria para las fixtures y proporcionarla explícitamente a la aplicación como `DATABASE_URL`. Ninguna fixture debe inferir una URL real de un `.env` del desarrollador. Antes de cualquier limpieza verificar host, puerto, nombre de base, PGDATA y marcador de propiedad del proceso de prueba. Cerrar conexiones, detener sólo ese clúster y retirar sólo el directorio creado por la ejecución. Si no se puede demostrar propiedad, detener limpieza y reportar.

Las fixtures crearán objetos auxiliares únicamente en esa DB aislada, sin tablas ficticias de producción. Para probar creación aditiva se puede inyectar metadata local del test con una tabla de prueba; limpiarla al final, sin contaminar `SQLModel.metadata` global. C-02 agregará los modelos reales y su aceptación relacional. No usar SQLite para la aceptación PostgreSQL. La documentación de [initdb 17](https://www.postgresql.org/docs/17/app-initdb.html) describe el clúster nuevo y sus parámetros de autenticación.

**Alternativas:** iniciar Docker sólo para pruebas requeriría habilitar un daemon hoy inaccesible; reutilizar la base instalada/credenciales existentes debilita el aislamiento. No se necesita ninguna de esas acciones con los binarios observados. Esta preparación local reversible no autoriza cambios en una base/VPS usada por otro proyecto.

### 3. Configuración diferida y explícita

`app/core/config.py` cargará `.env` local sin sobrescribir variables de entorno y construirá un objeto de configuración tipado dentro del startup. No crear motor ni validar configuración al importar módulos. Validar URL presente/no vacía y esquema `postgresql+asyncpg`; analizar con utilidades de URL de SQLAlchemy en lugar de separar manualmente credenciales. Proponer `SQL_ECHO` con default `false`, aceptar `true`/`false` sin distinguir mayúsculas y rechazar otro texto con mensaje propio. `env.example` tendrá sólo `postgresql+asyncpg://USUARIO:CLAVE@HOST:5432/BASE` y el ejemplo de diagnóstico. No agregar `pydantic-settings`: `python-dotenv`, tipado y validación pequeña cubren este alcance.

En pruebas de precedencia usar entorno controlado y `.env` en directorio temporal, nunca el archivo del usuario. La aplicación no tendrá URL de respaldo ni elegirá automáticamente la DB de test. Excluir `.env`, `.venv`, archivos temporales de PG y `.atl/` del control de versiones al preparar exclusiones locales; no modificar `.dockerignore` hasta C-07.

**Alternativas:** leer configuración a nivel de importación dificulta aislar tests y produce fallos antes de que el servidor gestione el startup. Aceptar silenciosamente un booleano mal escrito puede impedir obtener evidencia SQL cuando se solicita.

### 4. Lifespan como dueño del motor y fábrica

En `app/main.py` exponer `create_app()` y `app = create_app()` sin red. El lifespan con `asynccontextmanager` carga configuración, crea motor con `create_async_engine`, construye `async_sessionmaker(..., expire_on_commit=False)` y almacena ambos en `app.state` de esa instancia. `app/core/database.py` contiene utilidades pequeñas de inicialización y la dependencia de sesión. Evitar objetos globales de motor/sesión y evitar otro contenedor de servicios.

Antes del `yield`, ejecutar una conexión real mediante `async with engine.begin()`; importar el registro explícito de modelos y llamar `await connection.run_sync(SQLModel.metadata.create_all)`. Esa conexión prueba accesibilidad aun con metadata vacía. Mantener un punto central de imports en `app/modules/__init__.py` que cargue los módulos `models.py`; C-01 los deja sin entidades, C-02 declara las nueve tablas allí. `health/models.py` explica que salud no tiene tabla.

Envolver todo lo posterior a crear el motor en `try/finally` con `await engine.dispose()` para cubrir tanto startup fallido como apagado. Traducir errores de conexión a diagnóstico propio sin incluir URL, SQL o texto crudo del driver; no encadenar un error que vuelva a mostrar secretos en la salida. No atrapar indiscriminadamente errores de programación como si fueran indisponibilidad. La creación de tablas es aditiva: no agregar `drop_all`, resets ni cambios automáticos a columnas existentes.

**Alternativas:** un motor al importar hace difícil distinguir instancias/tests y controlar su cierre. Un heartbeat sin conexión real no cumpliría el fallo temprano requerido. [SQLAlchemy async 2.0](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm) documenta el puente async para metadata y el cierre del motor.

### 5. Sesión por petición con cierre garantizado

`get_session(request)` toma la fábrica de `request.app.state` y usa un contexto async para producir una `AsyncSession`. `Depends(get_session)` con caché normal de FastAPI permite que dependencias de la misma petición reciban el mismo objeto. Dos peticiones deben obtener objetos distintos, incluidas concurrentes. No utilizar `async_scoped_session` ni compartir una sesión entre tareas.

La dependencia gestiona duración, no decide commits. Los services futuros confirman/retroceden sus operaciones; al cerrar una sesión con transacción no confirmada se libera/retrocede ese trabajo. `expire_on_commit=False` permite consultar atributos ya cargados tras commit; no autoriza lazy loading. La evidencia combina pruebas de dependencia con rutas sólo de test, instrumentación y prueba PostgreSQL de transacción no confirmada; esas rutas no entran a `app` productiva.

**Alternativas:** commit automático en el final de cada petición oculta la atomicidad que deberán definir los services. Una sesión global mezcla transacciones; [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks) exige sesiones separadas para tareas concurrentes.

### 6. Salud con responsabilidades distintas

`health/router.py` define handlers `async def`; schemas contiene las salidas de salud y service hace la comprobación DB con sesión explícita. Registrar sólo el router health en este change; preparar los seis routers de negocio sin operaciones públicas ficticias.

`live` devuelve `{"estado":"vivo"}` directamente, sin depender de sesión. `ready` usa la sesión inyectada y `await session.execute(text("SELECT 1"))`; éxito responde `{"estado":"listo"}`. Propuesta concreta de PR-03/PA-07: indisponibilidad de conexión/consulta luego del startup se traduce a `HTTPException(503, detail="Base de datos no disponible")`; la respuesta queda `{"detail":"Base de datos no disponible"}`. Debe cubrir tanto fallo al adquirir conexión como durante ejecución, liberar recursos y permitir recuperación posterior. Clasificar errores esperados del límite DB sin devolver SQL ni capturar fallos de programación ajenos.

Esta es una **decisión propuesta para revisión**, no una aprobación ya obtenida ni un mandato del PDF. Un 503 permite al futuro healthcheck reconocer la caída; un 500 genérico pierde el contrato explícito y un 200 daría disponibilidad falsa. El startup sigue fallando si DB no estaba accesible desde el inicio: no se demuestra live iniciando una app sin DB. Para caída posterior usar una app ya iniciada y un doble del límite DB; añadir una comprobación real que interrumpa únicamente el clúster privado cuando la infraestructura de test lo permita.

### 7. Strict TDD y bucle de eventos coherente

Usar `tests/unit/`, `tests/integration/` y `tests/conftest.py`, conservando `test/*.http` para C-06. Elegir pytest-asyncio con modo estricto: tests `pytest.mark.asyncio`, fixtures async explícitas `pytest_asyncio.fixture`, scope y loop de función. App, cliente, motor, sesiones y teardown de cada caso vivirán dentro del mismo loop; no llevar pools entre loops ni compartir una instancia de app de scope sesión.

Usar `httpx.AsyncClient` con `ASGITransport` y `LifespanManager` explícito. HTTPX por sí solo no ejecuta startup/shutdown, como advierte [FastAPI](https://fastapi.tiangolo.com/advanced/async-tests/). La configuración de scopes sigue [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html); no mezclar decoradores AnyIO y pytest-asyncio. [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops) explica por qué un pool no debe pasar entre loops.

Para cada conducta: baseline si se toca código existente; prueba mínima RED ejecutada por la razón esperada; mínimo GREEN ejecutado; triangular con dos o más entradas/estados incluido borde hasta cubrir los escenarios; refactor sólo con tests verdes. Un proyecto sin pruebas tendrá baseline documentado como «sin suite previa», no «0 pruebas pasando». No implementar app antes del primer RED. Preparar runner/dependencias/fixtures antes de ese RED no equivale a implementar conducta productiva. Nombres Arrange/Act/Assert y parametrización de variantes; mocks sólo donde permitan provocar fallos/observar recursos, con PostgreSQL real como aceptación de la infraestructura.

| Conducta | Archivo previsto | Casos mínimos / evidencia |
|---|---|---|
| Configuración | `tests/unit/test_config.py` | Entorno sobre `.env`; sólo `.env`; falta/vacío/controlador inválido; booleanos y texto inválido; errores sin secreto |
| Startup/shutdown | `tests/integration/test_lifespan.py` y unidad del límite de recursos | Conexión real exitosa; rechazada; import sin red; dispose normal y por fallo parcial; dos instancias |
| Creación aditiva | `tests/integration/test_database.py` | Metadata de prueba crea tabla; segundo inicio conserva fila/estructura; metadata vacía verifica conexión |
| Sesión | `tests/integration/test_sessions.py` | Peticiones concurrentes distintas; reutilización interna; cierre normal/excepción y rollback sin commit; atributos disponibles después de commit |
| Salud | `tests/integration/test_health.py` | live sin SQL con DB disponible/caída posterior; ready 200, adquisición fallida, consulta fallida, recuperación |

Registrar comandos y resultados reales del ciclo en el resumen apply con `Task / Test File / Layer / Safety Net / RED / GREEN / TRIANGULATE / REFACTOR`; no llenar resultados por anticipado. La estructura vacía y documentación se revisan directamente, sin assertions tautológicas.

## Risks / Trade-offs

- [El runtime bundled puede cambiar de ubicación] → Usarlo sólo como intérprete local; instrucciones generales Python 3.12+, nunca importarlo o incrustar su ruta en la API.
- [venv/ensurepip o descarga de wheels no disponibles al aplicar] → Verificar creación e instalación antes del código; reportar error concreto y resolver sólo el prerrequisito faltante, sin instalar Python global por rutina.
- [PostgreSQL privado no puede arrancar o puerto ocupado] → Puerto libre y PGDATA único; si falla, mostrar log sanitizado y no tocar servicios ni bases ajenas.
- [Alpine usa musl; Windows no demuestra compatibilidad final] → Verificar wheels de las versiones elegidas ahora y build real en C-07; no afirmar Docker probado mientras daemon no responde.
- [create_all puede parecer migración] → Tests de conservación y documentación de que sólo crea faltantes; C-02 prueba esquema completo, sin resets de datos existentes.
- [Mocks de caída ocultan diferencias del driver] → Aceptación con PostgreSQL real y caída/recuperación del clúster privado; usar dobles para ramas concretas y cierre, no como sustituto de integración.
- [SQL_ECHO produce diagnóstico voluminoso] → Desactivado por defecto, activación local explícita; no guardar URLs/credenciales en evidencias.

## Migration Plan

1. Revisar esta propuesta y comenzar apply sólo por una solicitud posterior del usuario. Conservar todos los tasks pendientes hasta entonces.
2. Preparar entorno virtual, dependencias resueltas, runner y clúster privado; no hay una base existente que migrar en este change.
3. Implementar por los ciclos TDD de `tasks.md`, validar contratos y documentar arranque con `uvicorn app.main:app` para el grupo.
4. Cerrar recursos temporales de prueba y entregar evidencia real. Si se interrumpe la ejecución, detener únicamente el proceso/clúster cuya propiedad quedó registrada; no borrar datos externos.
5. C-02 completa imports/modelos y prueba las nueve tablas; C-07 valida el contenedor; C-08 inspecciona y revisa destino/puertos/base antes de operar en VPS.

## Open Questions

No hay una decisión técnica de C-01 diferida a investigación genérica. El 503 y `SQL_ECHO` están concretados arriba como propuestas de este change, pendientes de la revisión de sus artefactos. Destino de VPS, puerto público y base autorizada (PA-01/02), PATCH/NULL y seed conservan su resolución en los changes correspondientes; no cambian este diseño local.
