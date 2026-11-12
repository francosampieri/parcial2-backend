# Proposal

## Why

La fundación ya conecta la API con PostgreSQL y crea tablas registradas, pero los módulos de negocio todavía no declaran entidades. C-02 convierte el modelo del parcial en nueve tablas relacionadas, para que catálogo, clientes y ventas puedan construirse sobre una base que garantice referencias, unicidad e importes válidos.

## What Changes

- Declarar `Editorial`, `Genero`, `Autor`, `Libro`, `LibroAutor`, `Cliente`, `PerfilCliente`, `Venta` y `RenglonVenta` como tablas SQLModel en sus módulos existentes, conservando nombres y columnas de la consigna.
- Establecer PK, ocho FK, UNIQUE, CHECK e índices; usar `Decimal`/`NUMERIC` para dinero y fecha con zona horaria para ventas.
- Conectar ambos extremos de cada relación con `back_populates`; conservar rol/orden en el objeto `LibroAutor` y representar `Cliente.perfil` como objeto opcional.
- Hacer que el registro previo a `create_all` incluya las nueve tablas y verificar creación aditiva sobre PostgreSQL aislado, sin migraciones ni resets de datos existentes.
- Planificar pruebas de integridad, navegación precargada, rollback y conservación de datos bajo Strict TDD; adaptar la prueba temporal de C-01 que esperaba metadata vacía.

## Capabilities

### New Capabilities

- `relational-domain-models`: esquema del dominio, restricciones persistentes, tipos exactos y navegación bidireccional de sus asociaciones.

### Modified Capabilities

- `application-foundation`: sustituir el requisito temporal «Creación aditiva de tablas registradas» por «Creación aditiva de tablas del dominio». El registro previo al arranque deja de admitir el dominio vacío y debe contener las nueve tablas; se conservan la creación aditiva y el resto del ciclo de vida. La sustitución se declara como REMOVED/ADDED para retirar explícitamente el escenario temporal de C-01.

## Impact

Afecta los seis archivos `app/modules/{editoriales,generos,autores,libros,clientes,ventas}/models.py`, el registro `app/modules/__init__.py` si necesita ajustes y las pruebas de modelos/arranque. Se reutilizan SQLModel, SQLAlchemy async, asyncpg, pytest y el PostgreSQL privado ya preparados en C-01; no se proponen dependencias nuevas.

La gobernanza es MEDIO por integridad y relaciones. Este change no autoriza cambios en VPS ni en bases con datos reales. Quedan fuera CRUD, DTO HTTP, códigos 409/422, seed, cálculo del total, descuento de stock, políticas de borrado/cascadas y despliegue. Las decisiones de PATCH, NULL en contratos y mínimo de autorías se resuelven en sus changes posteriores. La ausencia de perfil se representa sin fila de perfil; la única columna de negocio marcada nullable por la tabla de la consigna es `libro.genero_id`.
