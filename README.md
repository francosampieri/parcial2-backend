# Librería — totones (2PRO1)

API académica de Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria.
C-01 construye configuración, ciclo de vida y consultas de salud. C-02 incorpora los modelos y tablas del dominio; C-03 incorpora las operaciones del catálogo. C-04 incorpora las rutas de clientes y su perfil opcional.

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

La estructura reserva los módulos `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes` y `ventas`, con responsabilidades separadas en `models`, `schemas`, `service` y `router`. Salud, catálogo, clientes y ventas exponen operaciones; la validación integral y los datos iniciales se incorporan en C-06.

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

Los textos usan `str` y las cantidades `int`. Los importes se trabajan con `Decimal`: precios `NUMERIC(10,2)` y total `NUMERIC(12,2)`, con dos cifras decimales almacenadas. Esto evita usar `float` para dinero. PostgreSQL puede redondear entradas con más de dos decimales; la API de libros rechaza esos precios para evitar un redondeo inesperado. La fecha de venta usa `datetime` con zona horaria. En las columnas persistidas, sólo `libro.genero_id` admite `NULL`. Los `id` simples pueden ser `None` en un objeto nuevo antes de que PostgreSQL los genere; no son nulos en la fila guardada.

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

La API acepta PostgreSQL 16+, mientras que el helper de integración prepara su propio clúster privado y verifica **PostgreSQL 17 o superior** (el proyecto se validó originalmente con 17). Para esa suite se requieren sus binarios `postgres`, `initdb`, `pg_ctl`, `createdb` y `psql`; no hace falta tener un servicio PostgreSQL corriendo. La variable real del helper es `PG_BIN`, que señala su directorio. En una instalación Windows habitual:

```powershell
$env:PG_BIN = Join-Path $env:ProgramFiles 'PostgreSQL\17\bin'
.\.venv\Scripts\python.exe -m pytest -q
```

Si PostgreSQL está en otra ubicación, ajustar únicamente `PG_BIN` al directorio correspondiente. En otra terminal con el entorno virtual activado, definir `PG_BIN` para esa instalación y ejecutar:

```sh
python -m pytest -q
```

El clúster privado escucha sólo en `127.0.0.1` y desactiva los sockets Unix, así que no depende de que exista `/run/postgresql`. En Linux, una configuración típica es `PG_BIN=/usr/bin python -m pytest -q`.

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

Consultar [CHANGES.md](CHANGES.md) para el alcance y las dependencias de los ocho changes, la [KB](knowledge-base/README.md) para requisitos y [AGENTS.md](AGENTS.md) para las reglas confirmadas. Clientes corresponde a C-04; ventas a C-05; validación integral/seed a C-06; contenedor a C-07 y publicación revisada a C-08. La entrega final es `Parcial_Cap1a4_totones.zip`, del grupo totones, curso 2PRO1.

La evidencia real de C-01 y sus ciclos TDD está en [TDD-C01](docs/evidencia/TDD-C01.md): 51 pruebas pasaron en PostgreSQL17 privado, con servidor Uvicorn real y recuperación tras caída de la base. La disponibilidad de wheels Windows/musl fue comprobada; el build Alpine se verifica en C-07.
## Operaciones del catálogo

`POST /editoriales/` recibe un objeto como `{"nombre":"Sur","pais":"Argentina"}`. El DTO `EditorialCreate` declara qué campos acepta la API y rechaza campos adicionales, incluido `id`; ese identificador lo genera la base. Una creación correcta responde **201** con la editorial creada. Si el nombre ya existe, PostgreSQL rechaza la escritura y el servicio revierte la transacción, devolviendo **409** sin detalles internos.

`GET /editoriales/` lista editoriales en orden de ID y acepta `limit` (1 a 100, por defecto 20) y `offset` (desde 0). `GET /editoriales/{id}` consulta una editorial. Para modificar sólo el país se puede enviar `PATCH /editoriales/{id}` con `{"pais":"Uruguay"}`: el nombre omitido se conserva. En estos campos `null` se rechaza con 422; un ID inexistente devuelve 404 y un nombre repetido devuelve 409.

`GET /editoriales/{id}/libros` lista los libros de esa editorial con la misma paginación. Devuelve una lista vacía para una editorial sin libros y 404 si la editorial no existe. La consulta precarga editorial y género de cada libro.

`POST /autores/` recibe `nombre` y `nacionalidad`; acepta autores con nombres iguales. `GET /autores/{id}` consulta un autor y `PATCH /autores/{id}` modifica solamente los campos enviados. En el PATCH no se acepta `null` ni campos no declarados.

`GET /autores/{id}/libros` devuelve una lista paginada con el rol y orden de cada participación del autor; dos autores pueden compartir el mismo orden.

`POST /libros/` recibe ISBN, título, precio, stock, `editorial_id`, `genero_id` opcional y una lista `autores` con `autor_id`, `rol` y `orden`. Se exige al menos un autor, según la interpretación del diagrama que aprobó el grupo. El precio debe ser positivo, representable en NUMERIC(10,2) y tener como máximo dos decimales; así no se guarda un importe redondeado sin aviso. El libro y sus autorías se confirman juntos; si un ID no existe o se repite el ISBN o el autor, la API hace rollback y responde 409.

### Rutas disponibles

| Recurso | Método y ruta | Propósito |
|---|---|---|
| Editoriales | `POST /editoriales/`, `GET /editoriales/` | Crear y listar |
| Editoriales | `GET /editoriales/{id}`, `PATCH /editoriales/{id}` | Consultar y modificar datos enviados |
| Editoriales | `GET /editoriales/{id}/libros` | Listar sus libros |
| Géneros | `POST /generos/`, `GET /generos/` | Crear y listar |
| Géneros | `GET /generos/{id}/libros` | Listar sus libros |
| Autores | `POST /autores/`, `GET /autores/{id}`, `PATCH /autores/{id}` | Crear, consultar y modificar datos enviados |
| Autores | `GET /autores/{id}/libros` | Listar libros con rol y orden de ese autor |
| Libros | `POST /libros/`, `GET /libros/`, `GET /libros/{id}`, `PATCH /libros/{id}` | Crear, buscar, consultar detalle y modificar |

Para crear un género, enviar por ejemplo `POST /generos/` con `{"nombre":"Novela"}`. Todas las altas responden **201** al guardar correctamente; el `id` lo asigna la base, por lo que no debe enviarse. Los contratos de entrada rechazan campos desconocidos con **422**, tanto en el objeto principal como en las autorías anidadas.

### Ejemplo de libro y lecturas

Crear primero una editorial y al menos un autor; usar sus IDs reales en el ejemplo. Opcionalmente crear un género y proporcionar su ID; omitir `genero_id` deja el libro sin género. Los valores siguientes son ilustrativos:

```http
POST /libros/
Content-Type: application/json

{
  "isbn": "9780000000001",
  "titulo": "Un libro de ejemplo",
  "precio": "25000.00",
  "stock": 5,
  "editorial_id": 1,
  "genero_id": 1,
  "autores": [{"autor_id": 1, "rol": "autor", "orden": 1}]
}
```

Los roles admitidos son `autor`, `coautor`, `traductor` e `ilustrador`, y `orden` debe ser al menos 1. Precio positivo y stock no negativo son obligatorios. El valor del precio puede enviarse como cadena decimal para expresar los centavos con claridad; por ejemplo, `"10.999"` se rechaza con **422**. La respuesta de creación incluye el libro con editorial, género opcional y autorías; `GET /libros/{id}` devuelve ese detalle. `GET /libros/` lista libros con editorial y género.

Los listados aceptan `limit` entre 1 y 100, por defecto 20, y `offset` desde 0, por defecto 0. Por ejemplo, `GET /libros/?limit=10&offset=10` solicita la segunda página de hasta diez resultados. También se pueden combinar `GET /libros/?titulo=ejemplo&genero_id=1`: el título busca una parte literal sin distinguir mayúsculas y filtra además por género. Los caracteres `%` y `_` se buscan literalmente. Una página o lista relacionada sin resultados es `[]` con **200** si el recurso padre existe.

### Actualización parcial y errores

En un `PATCH` se envían solamente los campos a cambiar. Por ejemplo, `PATCH /editoriales/1` con `{"pais":"Uruguay"}` conserva el nombre omitido. En el PATCH de libro, `{"titulo":"Otro título"}` conserva precio y demás campos; `{"genero_id":null}` quita el género, mientras que omitir `genero_id` lo conserva. Los campos obligatorios no aceptan `null`, y `autores` no se admite en PATCH: las autorías quedan como fueron creadas.

En general, **404** indica que no se encontró el recurso consultado; **422**, que la entrada o parámetros no cumplen el contrato; y **409**, que una escritura entró en conflicto con la integridad de la base, por ejemplo un ISBN repetido o un ID de autor inexistente al crear un libro. El servicio hace `rollback` ante el conflicto: deshace toda la transacción pendiente, de modo que no quedan un libro y solo algunas de sus autorías. La respuesta de error no incluye SQL ni detalles internos.

## Clientes y perfiles (C-04)

Un **cliente** guarda nombre y email para las operaciones de la librería; no representa una cuenta con inicio de sesión. Esta API no autentica usuarios. El email es único en PostgreSQL. `POST /clientes/` recibe, por ejemplo, `{"nombre":"Ana Pérez","email":"ana@example.com"}` y responde **201** con el `id` generado. El cuerpo no acepta `id` ni otros campos desconocidos (**422**). Si el email ya pertenece a otro cliente, la escritura responde **409** y el servicio revierte la transacción.

`GET /clientes/{id}` devuelve el cliente con `perfil` como objeto cuando existe y `null` cuando todavía no se creó. Un cliente inexistente responde **404**; un ID que no sea entero, **422**. La relación uno a uno se precarga con `joinedload`, de modo que serializar el perfil no dispara una consulta posterior.

`PATCH /clientes/{id}` modifica solamente los campos enviados. Por ejemplo, `{"nombre":"Ana María Pérez"}` cambia el nombre y conserva el email y el perfil. El service usa `exclude_unset=True` para distinguir **campo omitido** de **campo enviado**. `{"email":null}` y `{"nombre":null}` se rechazan con **422**; un campo desconocido también. Si el email nuevo ya existe, responde **409** con rollback y conserva los datos anteriores. Un cliente inexistente responde **404**.

Cada cliente puede tener **como máximo un perfil**. `perfil_cliente.cliente_id` es una FK a `cliente.id` y tiene una restricción `UNIQUE`; un cliente sin perfil no tiene fila en esa tabla. La ruta `POST /clientes/{id}/perfil` forma parte de C-04: el ID del cliente se toma de la URL y el cuerpo contiene `telefono` y `direccion`, por ejemplo `{"telefono":"1123456789","direccion":"Calle 123"}`. Responde **201** al crear; **404** si el cliente no existe; **409** si ya tiene perfil; y **422** para campos desconocidos o incompletos. La consulta de ventas del cliente se describe en la sección de ventas.

## Ventas y comprobantes (C-05)

Una **venta** registra un hecho: el cliente que compró y los renglones con el libro y la cantidad. No se edita ni se borra, no descuenta stock y no procesa pagos. La cabecera y sus renglones se crean juntos.

`POST /ventas/` recibe el ID de un cliente existente y al menos un renglón. Cada renglón lleva sólo `libro_id` y `cantidad`, por ejemplo:

```http
POST /ventas/
Content-Type: application/json

{
  "cliente_id": 2,
  "renglones": [
    {"libro_id": 1, "cantidad": 2},
    {"libro_id": 4, "cantidad": 1}
  ]
}
```

El precio, el subtotal, el total y la fecha **no viajan en la petición**: los calcula el servidor. Enviarlos, junto con `id` o cualquier campo desconocido, responde **422**. También son **422** una lista vacía, un libro repetido o una cantidad menor o igual que cero.

El service lee el cliente y todos los libros en una consulta agrupada, copia el precio vigente de cada libro y calcula `subtotal = cantidad × precio_unitario` y `total` como la suma de los subtotales. Los importes usan `Decimal` y las columnas `NUMERIC`; la fecha se genera con zona horaria. Si el cliente o alguno de los libros no existe, responde **409** con un mensaje propio y hace rollback: no queda una venta parcial. Un fallo de integridad al confirmar también se traduce a 409 sin mostrar SQL ni trazas.

Por ejemplo, dos ejemplares de un libro de 25000.00 y uno de 27000.00 producen:

```json
{
  "id": 2,
  "fecha": "2026-11-12T15:00:00Z",
  "total": "77000.00",
  "cliente": {"id": 2, "nombre": "Tomás Ríos", "email": "tomas@example.com"},
  "renglones": [
    {"libro_id": 1, "titulo": "Rayuela", "cantidad": 2, "precio_unitario": "25000.00", "subtotal": "50000.00"},
    {"libro_id": 4, "titulo": "Respiración artificial", "cantidad": 1, "precio_unitario": "27000.00", "subtotal": "27000.00"}
  ]
}
```

El precio copiado es **histórico**: si después se modifica el precio del libro, la venta conserva el importe y el subtotal originales. El renglón no anida la venta ni el cliente completo; así se evita una respuesta recursiva.

### Lecturas de ventas

| Método y ruta | Respuesta |
|---|---|
| `GET /ventas/` | Lista paginada de resúmenes: `id`, `fecha`, `total` y `cliente` |
| `GET /ventas/{id}` | Detalle con cliente y renglones con título, precio y subtotal |
| `GET /clientes/{id}/ventas` | Lista paginada de las ventas de ese cliente |

Los listados ordenan por `id` y aceptan `limit` entre 1 y 100 (por defecto 20) y `offset` desde 0; valores fuera de rango responden **422**. No incluyen los renglones para no multiplicar filas: el detalle es la ruta que los expone. Una lista vacía es `[]` con **200** cuando el cliente existe. `GET /clientes/{id}/ventas` responde **404** si el cliente no existe; un ID de ruta no entero responde **422** en cualquier ruta de detalle.

Las lecturas precargan el cliente y, en el detalle, los renglones con su libro. El número de consultas no crece con la cantidad de renglones: no hay carga perezosa durante la serialización.

### Aviso de comprobante

Después de confirmar la venta, el handler agenda con `BackgroundTasks` una función async que espera `await asyncio.sleep(0.5)` y escribe el comprobante en el log. La tarea se ejecuta después de enviar la respuesta y no recibe la sesión de la petición, que ya se cerró; sólo usa el `venta_id` y el total. Por eso no retrasa el **201** ni bloquea otras peticiones.

Ese aviso es una simulación académica dentro del proceso, no una cola persistente: si el proceso se reinicia antes de terminar, el mensaje puede perderse. Una cola externa (por ejemplo, un worker con Redis) sería la alternativa para garantizar entrega, pero queda fuera del alcance del parcial.


