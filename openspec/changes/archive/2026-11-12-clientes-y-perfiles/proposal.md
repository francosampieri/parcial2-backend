# Proposal

## Why

Las tablas de clientes y perfiles ya existen, pero aún no tienen contratos ni rutas HTTP. C-04 permite registrar clientes, consultar su perfil opcional y asociar un único perfil antes de implementar las ventas en C-05.

## What Changes

- Incorporar `ClienteCreate`, `ClienteUpdate`, `ClienteRead`, `PerfilCreate` y `PerfilRead` separados de las tablas, con entradas que rechazan campos desconocidos.
- Exponer `POST /clientes/`, `GET /clientes/{id}`, `PATCH /clientes/{id}` y `POST /clientes/{id}/perfil`; registrar el router en la aplicación.
- Devolver el perfil como objeto opcional, precargado, y traducir email repetido o segundo perfil a 409 con rollback; IDs inexistentes a 404 y entradas inválidas a 422.
- Verificar los contratos con pruebas HTTP y PostgreSQL privado bajo Strict TDD, más documentación didáctica.

## Capabilities

### New Capabilities

- `clientes-http`: registro, consulta y actualización parcial de clientes, y creación de un perfil único por cliente.

### Modified Capabilities

Ninguna. La integridad de tablas y relaciones existente sigue cubierta por `relational-domain-models`.

## Impact

Se modifican `app/modules/clientes/{schemas,service,router}.py`, el registro de rutas en `app/main.py`, pruebas HTTP de clientes y README. Se reutilizan `Cliente` y `PerfilCliente`, SQLModel, sesión asincrónica y PostgreSQL existentes. No se agregan dependencias, auth, reglas nuevas de formato de email, DELETE ni edición de perfil. `GET /clientes/{id}/ventas` queda para C-05.
