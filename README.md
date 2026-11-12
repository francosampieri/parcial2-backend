# Librería — totones (2PRO1)

API académica de Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria.
C-01 construye configuración, ciclo de vida y consultas de salud. C-02 incorpora los modelos y tablas del dominio; los endpoints de negocio se desarrollan en los siguientes changes.

## Preparación local

Requisitos: Python 3.12 o superior con `venv`/`pip` y una base PostgreSQL 16 o superior accesible. Se recomienda Python 3.12 para mantener la misma rama que la futura imagen del parcial. No es necesario Docker para desarrollar C-01.

Ejecutar desde la raíz del proyecto. En PowerShell, elegir el intérprete instalado que cumpla el mínimo; el siguiente ejemplo usa el disponible como `python`:

```powershell
$PythonExe = 'python'
& $PythonExe --version
& $PythonExe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item env.example .env
```

Si `python` no apunta a la versión elegida, reemplazar `$PythonExe` por su ejecutable. También se puede usar `py -3.12 -m venv .venv` si esa versión está registrada en el launcher. Si `.venv` ya está preparada, reutilizarla y comprobar su versión con `.\.venv\Scripts\python.exe --version`. Copiar `env.example` sólo al preparar el entorno por primera vez, sin sobrescribir un `.env` propio existente.

En Linux/macOS, los pasos equivalentes con un intérprete 3.12+ son:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp env.example .env
```

`requirements.txt` contiene dependencias de ejecución con versiones resueltas. `requirements-dev.txt` incluye esas dependencias y añade el runner y herramientas de pruebas; por eso basta instalar este último para desarrollar. Para ejecutar la API sin herramientas de desarrollo, instalar `requirements.txt`.

### Base y configuración

Crear o solicitar una **base propia de desarrollo**, con un usuario autorizado para conectarse y crear sus tablas. La aplicación no crea la base PostgreSQL ni usuarios: el servidor, la base y sus permisos deben estar preparados antes de arrancar. No reutilizar una base de otro proyecto para estas pruebas.

Editar el `.env` local con esa conexión. [env.example](env.example) contiene sólo marcadores ficticios:

```dotenv
DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@HOST:5432/BASE
SQL_ECHO=false
```

Reemplazar los marcadores por valores del entorno propio; si la contraseña contiene caracteres reservados de URL, codificarlos para una URL de conexión. El ejemplo no funciona sin esos reemplazos. `.env` y sus variantes privadas, `.venv`, `tmp/`, cachés y `.atl/` están excluidos de Git. No incluir credenciales en archivos compartidos.

El entorno tiene prioridad sobre `.env`. `DATABASE_URL` es obligatoria y debe usar `postgresql+asyncpg`; no hay base alternativa incorporada. `SQL_ECHO=false` desactiva diagnóstico SQL; acepta `true`/`false` sin distinguir mayúsculas. Otro texto impide arrancar. El diagnóstico SQL es una elección de C-01, no una exigencia textual del PDF.

Por ejemplo, una variable `DATABASE_URL` ya definida en la terminal sigue teniendo prioridad aunque se edite `.env`. `SQL_ECHO=true` permite observar las consultas durante el diagnóstico local; mantenerlo desactivado cuando no se necesite y sanitizar cualquier evidencia que se comparta.

## Ejecutar la API

Con la base disponible y `.env` configurado, en PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Con el entorno virtual activado, el comando portable es:

```sh
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`app.main:app` identifica el objeto FastAPI que Uvicorn sirve mediante ASGI, el protocolo entre el servidor y la aplicación async. La documentación interactiva queda en [Swagger UI local](http://127.0.0.1:8000/docs). Detener con `Ctrl+C` para ejecutar el cierre del ciclo de vida.

La configuración y la primera conexión se comprueban en **startup**, antes de servir peticiones. Si falta la dirección, es inválida o PostgreSQL no está disponible desde el inicio, el arranque falla. Importar `app.main` por sí solo no abre conexiones. El 503 de readiness corresponde a una caída **posterior a un arranque exitoso**.

## Consultas de salud

| Operación | Respuesta | Qué comprueba |
|---|---|---|
| `GET /health/live` | 200 `{"estado":"vivo"}` | El proceso puede responder; no ejecuta SQL ni necesita sesión |
| `GET /health/ready` | 200 `{"estado":"listo"}` | Una consulta nueva `SELECT 1` alcanzó PostgreSQL en esa petición |
| `GET /health/ready`, con DB caída después del startup | 503 `{"detail":"Base de datos no disponible"}` | La aplicación no está lista para operar con la base |

Se pueden consultar desde la documentación interactiva o PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/live
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

Estar **vivo** significa que el proceso responde; estar **listo** significa que también funciona su dependencia PostgreSQL. Después de una caída, live sigue respondiendo sin consultar la base; ready vuelve a 200 cuando recupera la conexión. El contrato 503 con mensaje propio se concreta en C-01; el PDF exige comprobar `SELECT 1` y responder 200 cuando la base está disponible.

## Cómo se organiza la aplicación

El recorrido de una petición que utiliza persistencia es:

```text
petición → router → Depends(get_session) → service → AsyncSession → PostgreSQL
```

- **FastAPI/router:** define la ruta HTTP, interpreta parámetros y delega el trabajo al service. Los handlers son `async def`: `await` permite esperar la operación de base sin bloquear el hilo con una llamada síncrona.
- **Lifespan:** delimita inicio y apagado. Crea el motor async y la fábrica de sesiones, los guarda en `app.state` y libera el motor al terminar, también si falla una parte del inicio.
- **Motor:** administra conexiones y su pool para una instancia de aplicación. No es una sesión ni una transacción de negocio.
- **Fábrica:** construye sesiones a pedido. `Depends(get_session)` obtiene una sesión para la petición y garantiza su cierre; peticiones distintas no comparten una `AsyncSession`.
- **Service/sesión:** el service recibe la sesión explícitamente y decide los futuros `commit`/`rollback`. La dependencia gestiona la duración, **sin commit automático al terminar cada petición**. El trabajo no confirmado se descarta al cerrar la sesión. `expire_on_commit=False` conserva los atributos ya cargados después de confirmar; no habilita lazy loading.

Antes de atender, se importan los modelos registrados y se ejecuta `create_all` con el motor async. Es una operación **aditiva**: crea tablas faltantes, no migra columnas de tablas existentes ni borra datos. Salud no necesita una tabla propia. Si una tabla existente es incompatible con el modelo, `create_all` no la actualiza: hay que analizar una migración antes de intervenir esa base. El arranque no ejecuta seed ni reset y no se implementan migraciones en este change.

La estructura reserva los módulos `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes` y `ventas`, con responsabilidades separadas en `models`, `schemas`, `service` y `router`. Actualmente sólo salud tiene operaciones públicas; el CRUD de negocio se implementará en los próximos changes.

## Modelo de datos

Una clase SQLModel declarada con `table=True` describe una tabla; una instancia representa una fila con la que trabaja Python. El objeto puede existir sólo en memoria: `flush` envía los cambios a la base dentro de la transacción, y `commit` los confirma. Los modelos están repartidos en los `models.py` de cada módulo:

| Módulo | Clase → tabla | Columnas |
|---|---|---|
| editoriales | `Editorial` → `editorial` | `id`, `nombre`, `pais` |
| generos | `Genero` → `genero` | `id`, `nombre` |
| autores | `Autor` → `autor` | `id`, `nombre`, `nacionalidad` |
| libros | `Libro` → `libro` | `id`, `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id` |
| libros | `LibroAutor` → `libro_autor` | `libro_id`, `autor_id`, `rol`, `orden` |
| clientes | `Cliente` → `cliente` | `id`, `nombre`, `email` |
| clientes | `PerfilCliente` → `perfil_cliente` | `id`, `cliente_id`, `telefono`, `direccion` |
| ventas | `Venta` → `venta` | `id`, `cliente_id`, `fecha`, `total` |
| ventas | `RenglonVenta` → `renglon_venta` | `id`, `venta_id`, `libro_id`, `cantidad`, `precio_unitario` |

Los textos usan `str` y las cantidades `int`. Los importes se trabajan con `Decimal`: precios `NUMERIC(10,2)` y total `NUMERIC(12,2)`, con dos cifras decimales almacenadas. Esto evita usar `float` para dinero. PostgreSQL puede redondear entradas con más de dos decimales; la validación de entradas se definirá en los contratos posteriores. La fecha de venta usa `datetime` con zona horaria. En las columnas persistidas, sólo `libro.genero_id` admite `NULL`. Los `id` simples pueden ser `None` en un objeto nuevo antes de que PostgreSQL los genere; no son nulos en la fila guardada.

### Claves, restricciones e índices

- **PK (clave primaria):** identifica una fila. La mayoría usa `id`; `libro_autor` usa la combinación `(libro_id, autor_id)`, por lo que la misma pareja no se repite.
- **FK (clave foránea):** apunta a una fila existente de otra tabla. Se ubica en la tabla dependiente; por ejemplo, muchos libros pueden compartir una editorial, por eso cada libro guarda `editorial_id`.
- **UNIQUE:** impide duplicados en `editorial.nombre`, `genero.nombre`, `libro.isbn`, `cliente.email` y `perfil_cliente.cliente_id`.
- **CHECK:** impone condiciones sobre una fila: precio y precio unitario mayores que cero, stock y total no negativos, cantidad y orden al menos uno, y rol en `autor`, `coautor`, `traductor` o `ilustrador`.
- **Índice:** estructura que permite buscar por columnas con mayor eficiencia, a cambio de espacio y trabajo en escrituras. Una FK no crea automáticamente su índice en PostgreSQL.

| FK en la tabla dependiente | Referencia | Índice para esa FK |
|---|---|---|
| `libro.editorial_id` | `editorial.id` | explícito |
| `libro.genero_id` | `genero.id` | explícito; la referencia es opcional |
| `libro_autor.libro_id` | `libro.id` | cubierto por el primer componente de la PK compuesta |
| `libro_autor.autor_id` | `autor.id` | explícito; es el segundo componente de la PK |
| `perfil_cliente.cliente_id` | `cliente.id` | cubierto por el índice UNIQUE |
| `venta.cliente_id` | `cliente.id` | explícito |
| `renglon_venta.venta_id` | `venta.id` | explícito |
| `renglon_venta.libro_id` | `libro.id` | explícito |

La PK y UNIQUE ya crean los dos índices indicados; crear otros iguales sería redundante. Estas reglas corresponden al modelo de la consigna y a la trazabilidad RN-01/02/03/09 y RT-DB-04 de la KB.

### Cómo se relacionan los objetos

En la **agregación**, una editorial se comparte entre libros: `libro.editorial` y `editorial.libros` representan ambos sentidos. Una **asociación** vincula entidades, como una venta y su cliente, o un renglón y su libro. `LibroAutor` es una asociación con datos propios: `libro.autorias[i].autor` accede al autor y la autoría conserva también `rol` y `orden`. La posición `i` es un índice de la colección cargada; no implica un orden estable garantizado por la consulta.

La relación venta/renglones se describe como **composición**: el renglón pertenece a la venta. Aquí se modelan su FK y su colección; el alta HTTP compuesta y el cálculo del total corresponden a C-05. Este modelo no añade una política de borrado en cascada. El perfil es uno a uno opcional: `cliente.perfil` es un objeto o `None`, no una lista; un cliente sin perfil simplemente no tiene fila en `perfil_cliente`.

`back_populates` enlaza los dos extremos del mapeo, pero no carga automáticamente cada relación inversa. En las consultas posteriores se deben precargar los caminos que se van a recorrer: `joinedload` para relaciones a uno y `selectinload` para colecciones. Esto evita consultas implícitas y el problema N+1 en sesiones asíncronas.

## Pruebas

La API acepta PostgreSQL 16+, mientras que el helper de integración actual prepara y verifica **PostgreSQL 17**. Para esa suite se requieren sus binarios `postgres`, `initdb`, `pg_ctl`, `createdb` y `psql`; no hace falta tener un servicio PostgreSQL corriendo. La variable real del helper es `PG_BIN`, que señala su directorio. En una instalación Windows habitual:

```powershell
$env:PG_BIN = Join-Path $env:ProgramFiles 'PostgreSQL\17\bin'
.\.venv\Scripts\python.exe -m pytest -q
```

Si PostgreSQL está en otra ubicación, ajustar únicamente `PG_BIN` al directorio correspondiente. En otra terminal con el entorno virtual activado, definir `PG_BIN` para esa instalación y ejecutar:

```sh
python -m pytest -q
```

pytest es el runner: descubre y ejecuta las pruebas; pytest-asyncio ejecuta las funciones async en modo estricto, con un loop por caso. Aplicación, cliente y conexiones async de cada caso permanecen en ese mismo loop. HTTPX hace peticiones ASGI dentro del proceso y LifespanManager ejecuta explícitamente startup/shutdown; HTTPX por sí solo no inicia el lifespan.

Para revisar específicamente esquema, restricciones, relaciones y arranque de los modelos, con `PG_BIN` configurada como arriba:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/integration/test_domain_schema.py tests/integration/test_domain_constraints.py tests/integration/test_domain_relationships.py tests/integration/test_database.py
```

Los escenarios y resultados observados durante C-02 se documentan en [TDD-C02](docs/evidencia/TDD-C02.md); los nombres de pruebas y esta instrucción no reemplazan la ejecución real.

Las fixtures crean un clúster nuevo bajo `tmp/pg-foundation-<id>`, con SCRAM, contraseña aleatoria efímera, puerto libre y escucha sólo loopback. Crean únicamente `libreria_test`; no usan el `.env` del usuario, servicios Windows ni bases existentes. Al terminar verifican ruta/propietario, detienen sólo ese clúster y eliminan su directorio. La suite incluye una caída y recuperación real de ese recurso. No ejecutar esta aceptación con SQLite ni apuntarla a datos reales.

La configuración de pytest reserva `tmp/pytest-foundation` para temporales del runner. No guardar trabajo personal allí: pytest gestiona y renueva ese directorio.

Strict TDD organiza el desarrollo: prueba conductual RED, implementación mínima GREEN, variantes que cubran al menos dos casos por comportamiento y refactor con pruebas verdes. Si se modifica código existente, primero se registra su baseline. Los resultados y la tabla de evidencia del ciclo se registran en el resumen de implementación a partir de ejecuciones reales; esta guía no anticipa un conteo final de pruebas. Los `.http` y las evidencias académicas se completan en sus changes y no se sustituyen por pytest.

## Continuación y fuentes

Consultar [CHANGES.md](CHANGES.md) para el alcance y las dependencias de los ocho changes, la [KB](knowledge-base/README.md) para requisitos y [AGENTS.md](AGENTS.md) para las reglas confirmadas. Catálogo y clientes continúan en C-03/C-04; ventas en C-05; validación integral/seed en C-06; contenedor en C-07 y publicación revisada en C-08. La entrega final es `Parcial_Cap1a4_totones.zip`, del grupo totones, curso 2PRO1.

La evidencia real de C-01 y sus ciclos TDD está en [TDD-C01](docs/evidencia/TDD-C01.md): 51 pruebas pasaron en PostgreSQL17 privado, con servidor Uvicorn real y recuperación tras caída de la base. La disponibilidad de wheels Windows/musl fue comprobada; el build Alpine se verifica en C-07.
