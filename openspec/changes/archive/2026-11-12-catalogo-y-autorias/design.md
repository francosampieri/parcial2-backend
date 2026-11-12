# Design

## Context

Ver `proposal.md` para el propósito. C-01 y C-02 dejaron lifespan, sesión asincrónica por petición, nueve modelos SQLModel y restricciones comprobadas en PostgreSQL; únicamente el router de health está registrado. Los módulos de catálogo tienen `schemas.py`, `service.py` y `router.py` vacíos. Las specs `application-foundation` y `relational-domain-models` siguen vigentes. La suite histórica fue de 169 pruebas verdes, pero debe ejecutarse como baseline real antes de modificar archivos existentes. El proyecto fue movido a `parcial2-backend`: verificar y preparar su entorno local sin asumir que un `.venv` movido funciona.

## Goals / Non-Goals

**Goals:** traducir los contratos de `catalogo-http` a HTTP y persistencia asincrónica manteniendo las garantías anteriores, con pruebas conductuales reales de PostgreSQL y carga anticipada.

**Non-Goals:** cambiar esquema o migrar datos, implementar ventas/clientes/seed, borrar entidades, implementar actualización de autorías, desplegar o modificar una base ajena. Los .http y evidencia integral se completan en C-06; las pruebas de este change se automatizan sin sustituirlos.

## Decisions

### 1. Router, servicio y DTO separados

Cada router valida HTTP y recibe `AsyncSession` mediante `Depends(get_session)`; delega en funciones async del servicio con sesión explícita. Los DTO Create/Update/Read son distintos de tablas; no incluyen id de entrada y usan `extra='forbid'` incluso anidados, por decisión previa del usuario. Registrar cuatro routers en `create_app` preservando salud/lifespan. Cada DTO de lectura incluye sólo relaciones previstas, evitando bucles recursivos.

**Alternativa:** usar los modelos de tabla directamente reduce código, pero permite exponer columnas y confunde contrato HTTP con esquema persistente.

### 2. PATCH, ausencia y null

`model_dump(exclude_unset=True)` distingue campos ausentes de enviados. Para editoriales, autores y libros se validan como no nulos los campos obligatorios aun siendo omisibles; sólo `genero_id: null` quita una relación. `autores` no forma parte de `LibroUpdate`; `extra='forbid'` lo rechaza con 422. Las autorías quedan inmutables en PATCH. El usuario eligió esta alternativa frente a reemplazar la colección completa; permite actualizar datos simples, a costa de no poder corregir autorías desde esta ruta.

**Alternativa:** declarar todos los campos `Optional` y hacer `exclude_none` confundiría ausencia con `null` e impediría quitar género; dejar `null` obligatorio hasta PostgreSQL lo convertiría en 409 en lugar del 422 elegido.

### 3. Entrada del libro y precisión

`LibroCreate` contiene una o más autorías anidadas, con FK y rol/orden; el mínimo interpreta la cardinalidad de figura 1 y fue aprobado por el usuario, no se atribuye a una frase textual del PDF. Validar precio `Decimal > 0`, máximo 10 dígitos y dos decimales, sin redondear, stock >= 0, rol y orden. El usuario aprobó rechazo 422 para más de dos decimales. Establecer y probar las formas concretas de entrada Decimal compatibles con el ejemplo de cadena; no usar float para persistir. No exigir ISBN matemáticamente válido, longitud de textos, autores únicos por orden, normalización u otras reglas ajenas.

**Alternativa:** delegar precio a NUMERIC puede redondear más de dos decimales silenciosamente. Un duplicado de autor se deja a la PK compuesta y produce 409, evitando reglas adicionales distintas de la base.

### 4. Escrituras atómicas y errores

Crear libro y sus `LibroAutor` por IDs sin SELECT previo de existencia ni de unicidad, con un único commit para toda el alta. Ante `IntegrityError`, rollback y respuesta propia 409 sin texto SQL/constraint/tabla. Aplicar la misma política para conflictos de las demás escrituras, sin preconsulta de unicidad. Consultar el recurso solicitado para PATCH/detalle y resolver 404 es diferente de prevalidar unicidad o FK del alta. Tras commit recargar explícitamente el detalle con grafo de precarga y `populate_existing` o equivalente si el mapa de identidad conserva relaciones no cargadas; no depender de lazy loading.

**Alternativa:** confirmar cada autoría por separado deja un libro parcial si una FK falla. Consultar IDs antes del alta añade viajes y viola explícitamente el ejercicio 4.

### 5. Consultas acotadas, orden y filtros

Precargar relaciones a uno con `joinedload` y colecciones con `selectinload`, incluyendo `LibroAutor.autor`; para respuesta libros por autor conservar rol/orden del vínculo del autor solicitado. Medir número de consultas para detalle con 1 y N autores en HTTP real con fixture privada; sin N+1 ni acceso lazy durante serialización. Ordenar listados por PK, autorías por `(orden, autor_id)` para desempates. Limitar listados a 1–100 (20 por defecto), offset >= 0 y 0 por defecto, incluso listados por padre; padre ausente 404, sin hijos 200 `[]`.

Búsqueda literal case-insensitive con expresión parametrizada: escapar `%`, `_` y escape antes del ILIKE/contiene si la biblioteca no lo hace, para tratar los caracteres ingresados como texto, no como comodines. Se documenta esta elección de implementación y se prueban parámetros de inyección, porcentajes, guiones bajos y filtros combinados.

**Alternativa:** interpolar texto en SQL es inseguro; acceder a autores en un bucle causa N+1. El orden implícito de filas puede cambiar entre páginas.

### 6. Pruebas y TDD sin repetir la desviación C-02

Ejecutar baseline antes de editar archivos existentes y detenerse ante fallas previas. Para cada conducta, escribir prueba y ejecutar RED por ausencia de la conducta esperada ANTES de producción, implementar mínimo GREEN, agregar caso distinto/borde y volver a ejecutar, luego refactor sólo en verde. Registrar evidencia real por tarea; no marcar completada si falta RED propio exigido, ni fabricar fallos retroactivos. Esto corrige la desviación procesal documentada en `docs/evidencia/TDD-C02.md`.

Usar HTTPX ASGITransport + LifespanManager y fixtures PostgreSQL privadas existentes; aislar datos por transacción o recursos propios y comprobar rollback a través de otra sesión. En conflictos observar ausencia de filas parciales, que la sesión se recupera y que no se devuelve diagnóstico interno. Instrumentar eventos SQL y clasificar consultas de negocio para comprobar no preconsultas y número fijo; no confundir SELECT posterior al commit para respuesta con prevalidación. Conservar las 169 pruebas previas, adaptando con evidencia y baseline cualquier expectativa temporal afectada.

## Risks / Trade-offs

- [Sesión con relaciones ya presentes sin precarga tras commit] → recargar explícitamente y probar serialización HTTP para 1 y varios autores.
- [PATCH omisión/null indistinguibles] → `exclude_unset` y validadores de campos enviados, pruebas para cada campo y ambos casos.
- [Errores de integridad filtran nombres internos] → traducir y verificar respuesta y rollback con PostgreSQL real.
- [Paginación y autores con empates inestables] → ordenar por claves estables y probar páginas y empates.
- [El SQLAlchemy/asyncpg real no coincide con mocks] → integración relacional real y contadores SQL; no usar SQLite como sustituto.
- [Crear base real accidentalmente] → fixtures privadas existentes, sin tocar `.env` ni datos de usuario/VPS; sin migración o resets.

## Migration Plan

Aplicar en checkout local y probar en PostgreSQL aislado. El cambio agrega routers sin modificar las tablas de C-02; una instalación con esquema compatible no necesita migración. Si un esquema real ya existente difiere, detenerse y planificar su evolución antes de tocar datos. Revertir código elimina estas rutas sin borrar tablas ni datos. La publicación y su revisión son posteriores.

## Open Questions

No quedan decisiones bloqueantes de C-03. La política de seed, VPS y fecha de entrega pertenecen a changes posteriores.
