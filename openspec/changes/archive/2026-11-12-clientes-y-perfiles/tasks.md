# Tasks

## 1. Referencia y aislamiento

- [x] 1.1 Ejecutar la suite existente con PostgreSQL privado antes de modificar archivos; registrar resultado real y detener una tarea afectada por fallas preexistentes. Verificar salida de pytest en `docs/evidencia/TDD-C04.md`.
- [x] 1.2 Preparar fixtures HTTP/datos de clientes aislados reutilizando `tests/conftest.py`; verificar con dos casos que el cleanup sólo afecta IDs propios y que no depende del orden de tests.

## 2. Alta y detalle de cliente

- [x] 2.1 Bajo RED→GREEN→triangulación, crear DTO de alta/lectura y `POST /clientes/` con 201; verificar dos clientes distintos, ID generado y rechazo 422 de ID/campos extra en pruebas HTTP reales.
- [x] 2.2 Bajo TDD, traducir email duplicado a 409 con rollback sin SQL visible; verificar cliente existente conservado, ausencia de fila parcial y alta válida posterior en PostgreSQL.
- [x] 2.3 Bajo TDD, incorporar `GET /clientes/{id}` con perfil objeto opcional precargado; verificar cliente sin perfil, con perfil, ID inexistente 404, ID no entero 422 y consultas sin lazy loading.
- [x] 2.4 Documentar en README alta, detalle, perfil opcional y diferencia entre cliente y usuario autenticado; verificar ejemplos contra pruebas y rutas implementadas.

## 3. PATCH de cliente

- [x] 3.1 Bajo RED→GREEN→triangulación, implementar `PATCH /clientes/{id}` con `exclude_unset`; verificar modificación de nombre/email por separado, preservación de campos omitidos y perfil, y 404 de cliente inexistente.
- [x] 3.2 Bajo TDD, rechazar `null` explícito en nombre/email y campos extra con 422, email duplicado con 409 y rollback; verificar datos previos intactos y respuesta sin detalles internos.
- [x] 3.3 Documentar en README omisión frente a `null`, ejemplo de PATCH parcial y códigos 404/409/422; comprobar que coincide con pruebas HTTP.

## 4. Perfil único

- [x] 4.1 Bajo RED→GREEN→triangulación, implementar `POST /clientes/{id}/perfil` con teléfono/dirección y cliente de URL; verificar 201, perfil como objeto al consultar cliente, 404 de cliente inexistente y 422 de `cliente_id`/id/campos extra o datos incompletos.
- [x] 4.2 Bajo TDD, traducir segundo perfil a 409 por UNIQUE con rollback; verificar primer perfil intacto, mensaje propio sin SQL y posibilidad de crear perfil para otro cliente.
- [x] 4.3 Verificar con cliente con y sin perfil la precarga de la relación escalar y número de consultas fijo; documentar en README FK única, uno a uno opcional y ausencia de edición/borrado de perfil.

## 5. Integración

- [x] 5.1 Registrar sólo las cuatro rutas C-04 en `app/main.py`; verificar esquema OpenAPI, handlers async y que `GET /clientes/{id}/ventas` permanezca reservado a C-05.
- [x] 5.2 Ejecutar suite completa, `pip check` y validación estricta OpenSpec; verificar regresiones del catálogo/salud, ausencia de clústeres PostgreSQL privados pendientes y completar tabla TDD con baseline, RED, GREEN, triangulación y refactor reales para cada tarea aplicable.
