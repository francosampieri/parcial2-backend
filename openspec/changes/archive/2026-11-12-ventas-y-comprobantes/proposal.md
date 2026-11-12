# Proposal

## Why

Las tablas `Venta` y `RenglonVenta` existen desde C-02, y el catálogo y los clientes ya exponen sus contratos HTTP, pero todavía no hay forma de registrar una venta completa. C-05 cierra ese flujo: confirma cabecera y renglones en una sola transacción, copia precios históricos y notifica el comprobante después de responder. Es el requisito que habilita la validación integral de C-06.

## What Changes

- Incorporar `VentaCreate` con `cliente_id` y `renglones` anidados (`libro_id`, `cantidad`), más `VentaRead`/`VentaDetail` con cliente y renglones calculados; las entradas rechazan precio, total, fecha, `id` y campos desconocidos.
- Exponer `POST /ventas/`, `GET /ventas/`, `GET /ventas/{id}` y `GET /clientes/{id}/ventas`, con listados paginados (`limit` 1–100, por defecto 20; `offset` desde 0).
- Validar al menos un renglón, cantidades mayores que cero y libros no repetidos; responder 422 ante contrato inválido.
- Leer los libros en una consulta agrupada, copiar sus precios con `Decimal`, calcular subtotales y total en el servidor, y fechar con zona horaria.
- Confirmar venta y renglones juntos; ante cliente o libro inexistente responder 409 con rollback, sin venta parcial. Conservar el precio copiado aunque luego cambie el libro.
- Precargar cliente y renglones (con título del libro) para el detalle y mantener un número fijo de consultas al variar la cantidad de renglones.
- Agendar con `BackgroundTasks` una función async que espera `asyncio.sleep(0.5)` y registra el comprobante en log después de la respuesta, sin reutilizar la sesión de la petición.
- Verificar los contratos con pruebas HTTP/PostgreSQL bajo Strict TDD, documentar límites en README y registrar la evidencia real de implementación.

## Capabilities

### New Capabilities

- `ventas-http`: alta atómica de ventas con renglones y precios históricos, consulta paginada de ventas, detalle y ventas por cliente, con aviso posterior de comprobante.

### Modified Capabilities

- `clientes-http`: se ajusta la cláusula que reservaba `GET /clientes/{id}/ventas` para C-05, para que el capability de clientes remita esa ruta a `ventas-http` sin contradecirla.

## Impact

Se completan `app/modules/ventas/{schemas,service,router}.py` y se registran sus rutas en `app/main.py`; se agregan pruebas HTTP/PostgreSQL, unitarias de DTO y documentación en README, junto con `docs/evidencia/TDD-C05.md` durante la implementación. Se reutilizan `Venta`, `RenglonVenta`, `Cliente`, `Libro`, SQLModel, la sesión asincrónica y PostgreSQL existentes. No se agregan dependencias, PATCH de ventas, alta suelta de renglones, descuento o control de stock, pagos, seed ni cambios de esquema.
