# Design

## Context

Ver `proposal.md`. C-02 ya definió `Cliente` y `PerfilCliente`, la FK única y la relación escalar opcional; C-03 dejó el patrón router/schema/service, sesión asincrónica por petición y pruebas HTTP con PostgreSQL privado. `app/modules/clientes/{schemas,service,router}.py` todavía no tiene comportamiento. Ver `specs/clientes-http/spec.md` para contratos observables.

## Goals / Non-Goals

**Goals:** Exponer los cuatro endpoints de clientes y perfil con entradas separadas, respuestas coherentes y lecturas sin lazy loading.

**Non-Goals:** Login, usuario autenticado, roles, borrado, edición de perfil y listado de ventas del cliente. La última ruta se incorpora en C-05 junto con ventas.

## Decisions

### Contratos separados y PATCH explícito

Definir DTO de entrada Create/Update con `extra='forbid'`; `ClienteCreate` exige nombre/email y `ClienteUpdate` acepta ambos opcionales sólo por omisión, rechazando `None` explícito. Aplicar `model_dump(exclude_unset=True)` para preservar campos no enviados. El usuario ya decidió para campos obligatorios que `null` responda 422. `PerfilCreate` exige teléfono/dirección; `cliente_id` procede del parámetro de ruta, sin permitirlo en el cuerpo. Mantener textos como `str`, sin normalización ni formato de email no exigidos.

**Alternativas:** Reutilizar modelos de tabla como entrada permite IDs o relaciones no declaradas; aceptar `null` llega a un NOT NULL y difiere la validación a la base; recibir `cliente_id` dos veces permitiría valores contradictorios.

### Operaciones en service y errores propios

Usar `AsyncSession` explícita en service y `Depends(get_session)` en handlers `async def`. Obtener un cliente antes de detalle/PATCH/alta de perfil para distinguir 404; no preconsultar email único ni segundo perfil. Confirmar altas/actualizaciones con `commit`; ante `IntegrityError`, hacer rollback y responder 409 con mensaje neutral sin SQL. `expire_on_commit=False` conserva atributos, pero relaciones de salida deben cargarse antes de serializar.

**Alternativas:** Preconsultar duplicados introduce una carrera entre comprobación e inserción. Capturar todos los errores de DB como 409 ocultaría errores de programación; limitar traducción a integridad. Crear repositorio/UoW agrega capas sin valor para cuatro rutas.

### Perfil escalar y precarga

El detalle y la respuesta PATCH/alta de perfil usan una consulta que precarga `Cliente.perfil` con `joinedload`; cliente sin fila de perfil se serializa como `null`, no como lista. `PerfilRead` no incluye un cliente anidado para evitar referencias recursivas. Las relaciones existentes de ventas quedan intactas, sin cargarlas para estos contratos.

**Alternativas:** Dejar la relación en lazy loading puede fallar bajo async o emitir SQL durante serialización. `selectinload` para una relación uno a uno suma consultas sin necesidad; `joinedload` reúne ambas filas.

### Pruebas y límites de la implementación

Antes de modificar archivos, confirmar baseline del repositorio nuevo con PostgreSQL privado. Para cada comportamiento, escribir y ejecutar un RED real antes de producción, luego GREEN y al menos dos casos distintos, incluidos bordes; refactorizar con suite verde. Probar HTTP y verificar filas/rollback desde otra sesión cuando corresponda. Comparar número de SQL en cliente con y sin perfil. Mantener los datos de prueba aislados y no tocar bases reales. Documentar resultados exactos y desviaciones en `docs/evidencia/TDD-C04.md`.

## Risks / Trade-offs

- [Respuesta intenta cargar perfil implícitamente] → Precarga explícita y prueba con SQL contado durante serialización.
- [Segundo perfil o email duplicado deja sesión fallida] → Rollback en `IntegrityError`, comprobar una escritura posterior válida.
- [PATCH con campo omitido pisa datos] → `exclude_unset` y pruebas separadas de omisión y `null`.
- [Crece el número de rutas previstas] → Verificar que C-04 registra cuatro y deja `GET /clientes/{id}/ventas` para C-05.

## Migration Plan

La implementación local reutiliza las tablas existentes sin cambiarlas. Registrar el router de clientes tras pasar las pruebas específicas; luego ejecutar la suite completa y validación OpenSpec. Un rollback de código a la versión anterior retira estas rutas sin borrar datos del esquema. No hay operación sobre VPS en este change.
