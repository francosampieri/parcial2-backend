# Design

## Context

Ver `proposal.md`. C-02 definió `Venta` y `RenglonVenta` con FK, CHECK e índices; C-03 y C-04 fijaron el patrón router/service/schema, la sesión asincrónica por petición, la precarga explícita y las pruebas HTTP con PostgreSQL privado. `app/modules/ventas/{schemas,service,router}.py` sigue vacío salvo los modelos, y `GET /clientes/{id}/ventas` quedó reservado para este change. Los contratos observables están en `specs/ventas-http/spec.md` y en el delta de `specs/clientes-http/spec.md`.

## Goals / Non-Goals

**Goals:** Completar el alta atómica y las tres lecturas de ventas, con contratos anidados, precios históricos y aviso posterior, sin duplicar capas ni tocar el esquema.

**Non-Goals:** PATCH o DELETE de ventas, alta suelta de renglones, descuento o validación de stock, pagos, seed, migraciones, autenticación y cambios en los modelos de C-02.

## Decisions

### DTO separados, anidados y calculados en servidor

`RenglonCreate` acepta sólo `libro_id` y `cantidad > 0`; `VentaCreate` acepta `cliente_id` y `renglones` con al menos un elemento. Ambos usan `extra='forbid'` y un validador de `VentaCreate` rechaza libros repetidos con 422 antes de tocar la base. `VentaRead` expone `id`, `fecha`, `total` y un `ClienteEnVenta` acotado a `id`/`nombre`/`email`; `VentaDetail` agrega `renglones` con `libro_id`, `titulo`, `cantidad`, `precio_unitario` y `subtotal`, sin anidar la venta dentro del renglón ni el perfil dentro del cliente.

**Alternativas:** Reutilizar `Venta` como entrada permite recibir precios o totales manipulables y relaciones no declaradas. Exponer el cliente completo obliga a precargar su perfil y agranda la respuesta sin necesidad. Calcular `subtotal` en el DTO de tabla mezcla persistencia con contrato.

### Alta transaccional con precios copiados

El service recibe la sesión explícita, consulta el cliente y todos los libros en una sola sentencia agrupada por `id`, y responde 409 propio si falta alguno. Esa consulta de precios es la lectura permitida por RN-06 y no una preconsulta de unicidad. Con los precios vigentes arma `RenglonVenta`, calcula subtotales y total con `Decimal`, fija `fecha = datetime.now(timezone.utc)`, agrega cabecera y renglones y confirma una sola vez. Ante `IntegrityError` hace rollback y responde 409; no hay commits por entidad.

**Alternativas:** Copiar el precio desde el DTO permite falsificar importes. Consultar libro por libro agrega consultas y facilita estados inconsistentes. Confirmar la cabecera antes de los renglones deja ventas parciales. Guardar `float` pierde exactitud monetaria.

### Forma de las lecturas y consultas acotadas

`POST` y `GET /ventas/{id}` devuelven `VentaDetail`, precargando cliente con `joinedload` y renglones con `selectinload` más el libro de cada renglón. `GET /ventas/` y `GET /clientes/{id}/ventas` devuelven `VentaRead` sin renglones: un resumen con `id`, `fecha`, `total` y cliente, ordenado por `id` y paginado con `Query`. Las ventas por cliente verifican primero la existencia del cliente (404) y luego listan sólo sus filas. Así el número de consultas es fijo y no crece con los renglones.

**Alternativas:** Incluir renglones en los listados multiplica filas y consultas sin que el contrato lo pida. Devolver sólo IDs obliga a otra llamada para mostrar el total. Ordenar por fecha agrega desempates innecesarios; `id` ya es estable.

### Ubicación de la ruta de ventas por cliente

`app/modules/ventas/router.py` define dos routers: uno con prefijo `/ventas` y otro con prefijo `/clientes` para `GET /{id}/ventas`. Ambos se registran en `app/main.py` después del router de clientes. La consulta vive en el service de ventas porque su contrato y su precarga son de ventas; el módulo de clientes no importa ventas ni duplica DTO.

**Alternativas:** Agregar la ruta al router de clientes acopla dos módulos y contradice la reserva explícita de C-04. Un módulo nuevo agrega una capa sin necesidad.

### Aviso posterior sin sesión

El handler de alta recibe `BackgroundTasks`, y sólo después de que el service confirma la venta agenda `service.avisar_comprobante(venta_id, total)` con valores primitivos. La función async ejecuta `await asyncio.sleep(0.5)` y escribe el comprobante con `logging`. No recibe la `AsyncSession` ni consulta la base, porque la sesión de la petición se cierra al terminar la respuesta. La tarea se ejecuta después de enviar el cuerpo, de modo que no retrasa el 201 ni bloquea otras peticiones.

**Alternativas:** Pasar la sesión a la tarea puede usarla cerrada o compartirla entre peticiones. `time.sleep` bloquearía el event loop. Una cola externa excede el alcance académico.

### Pruebas y ajuste de una prueba preexistente

La verificación combina unitarias de DTO para duplicados, cantidades y campos extra, e integración HTTP/PostgreSQL para totales, precios históricos, atomicidad, paginación, 404/409/422 y conteo de SQL. El aviso posterior se comprueba con un servidor uvicorn real para separar la llegada del 201 del log; el transporte ASGI puede esperar las tareas de fondo y no sirve para medir orden. La prueba OpenAPI de C-04 que exige exactamente cuatro rutas de clientes se actualiza para reconocer la quinta ruta, porque el contrato de clientes cambia en este change; la prueba funcional de las cuatro rutas de C-04 se conserva.

**Alternativas:** Simular `asyncio.sleep` acelera la suite pero no demuestra el orden real. Omitir el ajuste de la prueba OpenAPI produce una regresión falsa. Contar consultas con texto SQL es frágil; se usa el evento de SQLAlchemy ya empleado en C-03/C-04.

## Risks / Trade-offs

- [La prueba OpenAPI de C-04 falla al agregar la quinta ruta] → Ajustarla junto con el RED del nuevo contrato y conservar las aserciones de las cuatro rutas originales.
- [Serializar relaciones sin precarga emite SQL o falla en async] → Consultas explícitas y prueba de conteo fijo con distinta cantidad de renglones.
- [Una tarea de fondo usa la sesión cerrada] → Pasar sólo `venta_id` y `total`; probar con servidor real.
- [Precio del libro cambia entre la lectura y la confirmación] → Copia dentro de la misma transacción; el precio histórico queda fijado en el renglón y no se recalcula después.
- [Errores de integridad filtran detalles] → Traducir sólo `IntegrityError` a 409 neutral; el resto de errores de programación se propaga.
- [Los listados crecen con la cantidad de ventas] → `limit` acotado y offset; sin renglones anidados en el resumen.

## Migration Plan

No hay cambios de esquema ni migraciones: se reutilizan las tablas de C-02. La implementación agrega DTO, service y routers, y registra las dos rutas nuevas en `app/main.py`; luego se ejecuta la suite completa y la validación OpenSpec. Revertir el código retira las rutas sin borrar ventas ya persistidas. No hay operación sobre VPS en este change.
