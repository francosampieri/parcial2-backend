# Proposal

## Why

La API ya implementa las 26 operaciones, pero la entrega necesita datos de ejemplo reproducibles, casos HTTP ejecutables y evidencia integral verificable. C-06 reúne esas piezas sin volver a construir las rutas ni repetir pruebas unitarias existentes.

## What Changes

- Agregar un comando explícito de seed que cree sólo los datos faltantes usando claves naturales y conserve las filas existentes; nunca ejecutar seed al arrancar ni borrar datos.
- Preparar `test/*.http` para los casos C-01 a C-08 del PDF, con respuestas esperadas e IDs reales devueltos por el seed o creados durante el recorrido.
- Verificar una secuencia integral sobre PostgreSQL aislado: catálogo, cliente, perfil y venta de dos renglones con total exacto y precio histórico; reutilizar los 269 tests existentes y cubrir sólo huecos reales.
- Guardar evidencia real y sanitizada de C-07: número fijo de consultas para detalle de libro y venta con distinta cantidad de autores y renglones.
- Consolidar README para instalación desde cero, seed, pruebas y demostración, con grupo totones, integrantes y 2PRO1.

## Capabilities

### New Capabilities

- `reproducible-demonstration`: seed seguro, recorrido HTTP y evidencia reproducible del parcial.

### Modified Capabilities

Ninguna. Las rutas y sus contratos ya están definidos en las specs de catálogo, clientes y ventas.

## Impact

Agrega un comando local de seed, archivos `test/*.http`, evidencia en `docs/evidencia/` y ajustes al README. La base de prueba es PostgreSQL privado; no se autorizan resets ni cambios en VPS. No añade endpoints ni dependencias de aplicación. Gobernanza MEDIO por datos iniciales.
