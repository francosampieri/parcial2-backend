# Proposal

## Why

La aplicación ya dispone de tablas y relaciones del dominio, pero sólo expone rutas de salud. Para usar el catálogo desde HTTP hacen falta contratos, lógica de acceso y respuestas que apliquen las reglas del parcial sin perder la integridad relacional.

## What Changes

- Implementar las 16 operaciones de editoriales, géneros, autores y libros enumeradas en C-03, con DTO separados, servicios asincrónicos y routers registrados.
- Dar de alta libros con una o más autorías en una única transacción, sin comprobar previamente la existencia de FK o unicidad; traducir conflictos de la base a 409 sin filtrar detalles internos.
- Aplicar PATCH sólo a campos enviados: la autoría no se edita por esta ruta; únicamente `genero_id` admite `null` para quitar el género. Las decisiones fueron aprobadas por el usuario.
- Validar precio positivo y de hasta dos decimales, stock no negativo y autorías válidas; el mínimo de un autor refleja una interpretación confirmada del diagrama, no una frase textual de la consigna.
- Paginar listados, filtrar títulos con parámetros ligados y precargar las relaciones devueltas, sin consultas que crezcan con la cantidad de autores.
- Incorporar pruebas TDD de rutas, transacciones, errores, filtros, relaciones y regresión con PostgreSQL aislado; explicar los contratos en README.

## Capabilities

### New Capabilities

- `catalogo-http`: contratos HTTP para editoriales, géneros, autores, libros y sus relaciones, con validación, paginación y consistencia transaccional.

### Modified Capabilities

Ninguna: el esquema y las garantías persistentes existentes se conservan; se añade una capacidad HTTP sobre ellas.

## Impact

Afecta `schemas.py`, `service.py` y `router.py` en los cuatro módulos de catálogo, registro de routers en `app/main.py`, pruebas y README. Utiliza infraestructura y dependencias existentes. Cubre C-01, C-02 (ISBN), C-04 y C-08 del PDF y el lado libro de C-07; la evidencia integral sigue en C-06. No incluye clientes, ventas, seed, Docker o despliegue, ni operaciones DELETE o cambios de autorías vía PATCH. La gobernanza es MEDIO por lógica y transacciones.
