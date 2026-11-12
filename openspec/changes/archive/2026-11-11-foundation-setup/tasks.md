# Tasks

Cada tarea de comportamiento sigue Strict TDD: baseline de archivos existentes (si falla, detener e informar); RED ejecutado por la razón esperada antes de código productivo; mínimo GREEN; triangulación de al menos dos casos incluido borde hasta cubrir todos sus escenarios; refactor sólo con ejecución verde. Registrar evidencia real por task. Preparar herramientas y documentación no requiere tests artificiales. Todas las tareas permanecen pendientes al terminar la propuesta.

## 1. Entorno y runner aislados

- [x] 1.1 Crear `.venv` local con el intérprete Python 3.12 verificado, sin modificar instalaciones globales; verificar versión del intérprete de `.venv` y funcionamiento de pip/venv. Si falla ensurepip, reportar el prerrequisito concreto antes de seguir.
- [x] 1.2 Resolver e instalar en `.venv` el stack con los mínimos del diseño y `pytest`, `pytest-asyncio`, `httpx`, `asgi-lifespan`; registrar versiones resueltas en `requirements.txt` y `requirements-dev.txt`, comprobar `pip check`, imports y versión del runner, y comprobar metadatos/wheels de las extensiones para CPython 3.12 Windows y musllinux. Registrar la evidencia sin afirmar un build Alpine; no agregar compiladores por rutina.
- [x] 1.3 Preparar configuración pytest estricta y fixtures bajo `tests/conftest.py`, loop de función y entorno controlado; comprobar que el runner descubre una prueba conductual mínima del siguiente grupo y produce el RED esperado, sin implementar aún la aplicación ni añadir pruebas tautológicas de instalación. Registrar «sin suite previa» si sigue sin existir baseline.
- [x] 1.4 Preparar PostgreSQL 17 privado con PGDATA único bajo `tmp/pg-foundation-<id>`, marcador de propiedad, puerto loopback libre y autenticación SCRAM con contraseña efímera no impresa; crear sólo `libreria_test` en ese clúster y verificar versión/conexión SQL real y propiedad del destino. Preparar fixtures de cierre/limpieza acotada que se nieguen a tocar un destino ajeno; no reutilizar el `.env` del usuario ni servicios Windows.
- [x] 1.5 Entregar instrucciones locales iniciales en `README.md` y exclusiones `.gitignore` para `.env`, `.venv`, cachés, temporales de PG y `.atl/`; verificar los comandos de entorno/runner con Python 3.12+ sin rutas personales y que ningún archivo privado queda como entregable. Explicar runner y base aislada; no crear Dockerfile ni hacer commit/push.

## 2. Configuración explícita

- [x] 2.1 Escribir y ejecutar RED de `tests/unit/test_config.py` para lectura de dirección y precedencia; implementar configuración tipada diferida en `app/core/config.py` con `python-dotenv`, confirmar GREEN y triangular entorno sobre `.env`, sólo `.env`, falta, vacío, URL mal formada y controlador no permitido; comprobar diagnóstico propio sin secretos y ausencia de dirección fallback.
- [x] 2.2 Añadir RED del control `SQL_ECHO`, implementar mínimo y confirmar GREEN; triangular omisión, `false`, `TRUE` y valor inválido, y verificar que el motor recibirá el booleano interpretado. Ejecutar la suite de configuración tras cualquier refactor.
- [x] 2.3 Entregar `env.example` sólo con marcadores ficticios y actualizar README explicando prioridad del entorno, requisito de PostgreSQL, `SQL_ECHO` y protección del `.env`; verificar por revisión directa ejemplos sin credenciales reales y ejecutar los comandos documentados únicamente con configuración privada de prueba.

## 3. Aplicación, ciclo de vida y creación aditiva

- [x] 3.1 Escribir RED de importación sin red y startup con configuración válida/inválida en `tests/integration/test_lifespan.py`; implementar `create_app()`, `app` y esqueleto obligatorio de los siete módulos con `models/schemas/service/router` e imports de paquete. Confirmar GREEN y triangular import sin URL/DB, startup con PostgreSQL privado y startup sin URL; revisar estructura directamente y mantener seis módulos de negocio sin entidades ni operaciones ficticias.
- [x] 3.2 Escribir RED del motor/fábrica por instancia y fallo de conexión; implementar en lifespan y `app/core/database.py` creación async en `app.state`, `expire_on_commit=False` y conexión inicial real. Confirmar GREEN con DB accesible/inaccesible, metadata vacía y dos instancias independientes, incluso sin consultas de dominio; verificar que el startup fallido no sirve peticiones ni muestra credenciales.
- [x] 3.3 Escribir RED de cierre normal y fallo parcial de startup; implementar `dispose` en `finally` y traducción limitada de errores DB sin SQL/URL/trazas del driver. Confirmar GREEN y triangular apagado, fallo de conexión y fallo de inicialización posterior a crear motor; verificar recursos cerrados y ausencia de secretos en diagnósticos con dobles del límite DB y aceptación real PostgreSQL.
- [x] 3.4 Escribir RED de creación aditiva en `tests/integration/test_database.py` usando metadata de prueba aislada; preparar imports de modelos antes de `run_sync(create_all)` y confirmar GREEN. Triangular tabla faltante, arranque repetido con fila/estructura conservadas y registro vacío; no introducir las nueve tablas de C-02, no contaminar metadata global ni ejecutar resets de una base ajena.
- [x] 3.5 Actualizar README con `uvicorn app.main:app`, FastAPI/ASGI, `async/await`, lifespan, app.state, startup fallido y límite de `create_all`; verificar arranque y apagado con la base privada y que la explicación distingue motor/fábrica/sesión y no promete migraciones ni nueve tablas ya creadas.

## 4. Sesión por petición

- [x] 4.1 Escribir RED de `tests/integration/test_sessions.py` con rutas auxiliares sólo del test; implementar `Depends(get_session)` y contexto async con la fábrica de app.state. Confirmar GREEN y triangular dos peticiones concurrentes con sesiones distintas y reutilización de la sesión dentro de una misma petición; verificar sin rutas de prueba públicas en la aplicación.
- [x] 4.2 Añadir RED de liberación/rollback ante salida normal y excepción con trabajo sin confirmar; implementar sólo el manejo de duración necesario, confirmar GREEN y verificar en PostgreSQL privado que ambos caminos cierran recursos y no persisten escrituras sin commit automático. Triangular lectura de atributos cargados después de commit explícito sin consulta implícita; ejecutar suite de sesiones tras refactor.
- [x] 4.3 Documentar en README el recorrido petición → dependencia → service → sesión y quién decide commit/rollback; verificar que el ejemplo didáctico respeta una sesión por petición, no comparte sesiones entre tareas ni agrega UoW/repositorios.

## 5. Salud y disponibilidad

- [x] 5.1 Escribir RED de live en `tests/integration/test_health.py` con lifespan realmente ejecutado; implementar schemas/router health y `GET /health/live`, confirmar GREEN y triangular DB disponible y caída posterior a startup correcto. Verificar respuesta exacta 200 `{"estado":"vivo"}`, cero SQL y cero sesiones de esa operación; no iniciar una aplicación sin DB para eludir el contrato de startup.
- [x] 5.2 Escribir RED de ready y comprobación por petición; implementar service con sesión explícita y `SELECT 1`, confirmar GREEN y triangular consultas repetidas con respuesta exacta 200 `{"estado":"listo"}`. Verificar ejecución nueva por petición y cierre de su sesión.
- [x] 5.3 Añadir RED para indisponibilidad posterior al startup; implementar la propuesta 503 `{"detail":"Base de datos no disponible"}`, confirmar GREEN y triangular fallo al adquirir conexión, fallo al ejecutar consulta y recuperación posterior con 200. Verificar que no se filtran SQL/trazas/URL ni se capturan errores de programación como caída DB; ejecutar caída/recuperación real deteniendo únicamente el clúster privado y complementar con dobles para ramas concretas.
- [x] 5.4 Documentar los dos contratos health y explicar «proceso vivo» frente a «listo para operar», incluido 503 y fallo de startup; verificar ejemplos de respuestas contra las pruebas ya ejecutadas y señalar que 503/SQL_ECHO fueron propuestos en este change, no impuestos por el PDF.

## 6. Comprobación integrada y evidencia

- [x] 6.1 Ejecutar la suite completa de C-01 sobre PostgreSQL privado y revisar estructura/imports/dependencias conjuntamente; verificar ausencia de llamadas bloqueantes, código de dominio anticipado, URL de respaldo, secretos y tablas ficticias de producción. Registrar comandos/salidas reales; no ejecutar Docker/VPS ni afirmar cobertura de C-02 o casos D de despliegue.
- [x] 6.2 Entregar resumen didáctico y tabla de evidencia `Task / Test File / Layer / Safety Net / RED / GREEN / TRIANGULATE / REFACTOR`, con casos realmente ejecutados, limitaciones y prerrequisitos concretos restantes; verificar cada escenario de las dos specs contra su evidencia y marcar tareas sólo después de esa comprobación.
- [x] 6.3 Cerrar sesiones/clientes/motores y detener/limpiar sólo los recursos privados creados para pruebas, verificando ruta absoluta y marcador de propiedad antes de borrar. Comprobar que no quedan procesos de ese clúster ni artefactos con contraseñas; conservar únicamente evidencia sanitizada y no modificar servicios/datos ajenos.
















