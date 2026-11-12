# Tasks

## 1. Referencia, aislamiento y contratos de entrada

- [x] 1.1 Ejecutar la suite existente con PostgreSQL privado antes de modificar archivos; registrar la salida real (baseline esperado: 227 pruebas) en `docs/evidencia/TDD-C05.md` y detener una tarea afectada por fallas preexistentes, sin repararlas por cuenta propia.
- [x] 1.2 Preparar fixtures de ventas reutilizando `tests/conftest.py` y los seeds de catálogo/clientes; verificar con dos casos que cada prueba crea y retira sólo sus propias ventas, renglones y libros, en el orden que respeta las FK, y que no depende del orden de ejecución.
- [x] 1.3 Bajo RED→GREEN→triangulación, definir `RenglonCreate` y `VentaCreate` con `extra='forbid'`; verificar en `tests/unit/test_venta_dto.py` que se rechazan 422 renglones vacíos, `libro_id` repetido, cantidad cero o negativa, `precio_unitario`, `subtotal`, `total`, `fecha`, `id` y campos desconocidos, aceptando en cambio uno y varios renglones válidos.

## 2. Alta atómica de venta

- [x] 2.1 Bajo TDD, implementar `POST /ventas/` con `VentaRead`/`VentaDetail` y respuesta 201; verificar en `tests/integration/test_sale_http.py` el alta de dos renglones con `id`, `fecha`, `total`, cliente acotado y renglones con `libro_id`, `titulo`, `cantidad`, `precio_unitario` y `subtotal`, sin anidar la venta en el renglón.
- [x] 2.2 Bajo TDD, copiar precios desde la base con `Decimal`, calcular subtotales y total, y generar la fecha con zona horaria; triangular con dos libros de precios distintos (por ejemplo 25000.00 × 2 y 27000.00 × 1 → 77000.00) y comprobar la forma serializada de los importes.
- [x] 2.3 Bajo TDD, confirmar venta y renglones en una única transacción; verificar 409 propio y ausencia total de filas, observada desde otra sesión, cuando falta el cliente o uno de los libros, y una venta válida posterior con la aplicación recuperada.
- [x] 2.4 Bajo TDD, traducir un `IntegrityError` real de confirmación a 409 con rollback y mensaje sin SQL ni trazas; verificar que no queda cabecera parcial y que una escritura válida posterior funciona.
- [x] 2.5 Bajo TDD, conservar el precio histórico: registrar una venta, modificar después el precio del libro por PATCH y verificar que `GET /ventas/{id}` mantiene el precio y subtotal originales en el renglón.
- [x] 2.6 Documentar en README el contrato de `POST /ventas/`, los campos calculados que no viajan, la transacción conjunta, el 409 por referencias y la conservación de precios; cotejar los ejemplos con las pruebas verdes.

## 3. Consultas de ventas

- [x] 3.1 Bajo RED→GREEN→triangulación, implementar `GET /ventas/` paginado con `limit` 1–100 (por defecto 20), `offset >= 0` y orden estable por `id`; verificar resúmenes con `id`, `fecha`, `total` y cliente, lista vacía y 422 de paginación inválida.
- [x] 3.2 Bajo TDD, implementar `GET /ventas/{id}` con cliente y todos los renglones precargados; verificar 200 con títulos y subtotales, 404 de ID inexistente y 422 de ID no entero.
- [x] 3.3 Bajo TDD, implementar `GET /clientes/{id}/ventas` con la misma paginación; verificar que devuelve sólo las ventas del cliente, lista vacía para cliente sin ventas, 404 de cliente inexistente y 422 de ID no entero.
- [x] 3.4 Bajo TDD, comprobar que las lecturas no emiten consultas implícitas y que el número de SQL es fijo al comparar ventas con dos y con muchos renglones; registrar el conteo real de listado, detalle y ventas por cliente.
- [x] 3.5 Documentar en README las tres lecturas, la diferencia entre resumen y detalle, la paginación y por qué los listados no anidan renglones; cotejar rutas y respuestas con las pruebas.

## 4. Aviso de comprobante

- [x] 4.1 Bajo TDD, agendar con `BackgroundTasks` una función async que ejecute `await asyncio.sleep(0.5)` y registre el comprobante en el log con `venta_id` y total, sólo después de una venta confirmada; verificar que no recibe ni reutiliza la sesión de la petición.
- [x] 4.2 Verificar con servidor uvicorn real que el 201 llega antes de que termine el aviso y que otra petición se atiende durante la espera; comprobar que un alta rechazada no agenda la tarea, en `tests/integration/test_sale_http.py` o un archivo específico.
- [x] 4.3 Documentar en README la diferencia entre tarea posterior a la respuesta y una cola externa, y el motivo para no pasar la sesión a la tarea; cotejar con la prueba de orden y concurrencia.

## 5. Registro, regresión y cierre

- [x] 5.1 Registrar en `app/main.py` los routers de ventas y de ventas por cliente; actualizar la prueba OpenAPI de C-04 que exigía exactamente cuatro rutas de clientes para reconocer la quinta, conservando las cuatro originales, y verificar que las cuatro operaciones de ventas son async y que no existe PATCH de ventas ni alta suelta de renglones.
- [x] 5.2 Ejecutar la suite completa, `pip check` y `openspec validate ventas-y-comprobantes --strict`; comprobar regresión de catálogo, clientes y salud, ausencia de directorios `tmp/pg-foundation-*` pendientes y completar la tabla `Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR` con resultados reales en `docs/evidencia/TDD-C05.md`.
- [x] 5.3 Marcar C-05 en `CHANGES.md` sólo si el alcance quedó implementado y verificado; dejar el change listo para revisión y archivado posterior, sin publicar, commit ni push por cuenta propia.
