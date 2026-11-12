# Spec Delta

## Purpose

Permitir registrar y consultar clientes de la librería y asociarles un perfil opcional único mediante contratos HTTP comprobables.

## ADDED Requirements

### Requirement: Alta y lectura de cliente

La API SHALL exponer `POST /clientes/` y `GET /clientes/{id}`. El alta SHALL recibir `nombre` y `email` sin `id` y responder 201 con identificador y datos guardados. El detalle SHALL responder 200 con un campo `perfil` que sea un objeto o `null`; un cliente inexistente SHALL responder 404 y un ID de ruta no entero SHALL responder 422. El email SHALL ser único mediante la restricción de la base; un duplicado SHALL responder 409 con mensaje propio y rollback.

#### Scenario: Alta y detalle sin perfil
- **WHEN** se crea un cliente válido y se consulta su ID antes de agregar un perfil
- **THEN** el alta responde 201 y el detalle 200 con `perfil: null`

#### Scenario: Email duplicado
- **WHEN** se intenta crear un segundo cliente con el mismo email
- **THEN** la API responde 409 sin detalles SQL y permite otra escritura válida tras rollback

#### Scenario: ID inexistente o inválido
- **WHEN** se consulta un ID entero inexistente o una ruta con ID no entero
- **THEN** responde 404 o 422 respectivamente

### Requirement: Actualización parcial de cliente

La API SHALL exponer `PATCH /clientes/{id}` para `nombre` y `email`. SHALL actualizar sólo los campos enviados y conservar los omitidos y el perfil. `null` explícito en cualquiera de ambos campos obligatorios o un campo desconocido SHALL responder 422 sin modificar datos. Email repetido SHALL responder 409 con rollback; cliente inexistente SHALL responder 404. La respuesta válida SHALL incluir el perfil opcional.

#### Scenario: Modificar sólo nombre
- **WHEN** se envía PATCH con sólo `nombre` a un cliente existente
- **THEN** cambia el nombre y conserva email y perfil

#### Scenario: Nulo y campo extra
- **WHEN** se envía `email: null`, `nombre: null` o una propiedad no declarada
- **THEN** responde 422 y el cliente conserva sus datos previos

#### Scenario: Email en conflicto
- **WHEN** se cambia el email a uno que ya pertenece a otro cliente
- **THEN** responde 409 sin detalles internos y el valor anterior permanece almacenado

### Requirement: Perfil único para cliente existente

La API SHALL exponer `POST /clientes/{id}/perfil` con `telefono` y `direccion` obligatorios, tomando el cliente de la URL. SHALL responder 201 con el perfil creado. Un cliente inexistente SHALL responder 404; un segundo perfil para el mismo cliente SHALL responder 409 por la restricción única de la base, con rollback y mensaje propio. El detalle de cliente SHALL devolver el perfil como objeto opcional y sin carga perezosa.

#### Scenario: Primer perfil
- **WHEN** se crea un perfil válido para un cliente sin perfil y se consulta al cliente
- **THEN** responde 201 con el perfil y el detalle del cliente lo incluye como objeto

#### Scenario: Segundo perfil
- **WHEN** se intenta crear otro perfil para el mismo cliente
- **THEN** responde 409 sin SQL ni traza y conserva el primer perfil

#### Scenario: Cliente sin perfil o inexistente
- **WHEN** se consulta un cliente sin perfil o se intenta agregar perfil a ID inexistente
- **THEN** el detalle muestra `perfil: null` o el alta responde 404, respectivamente

### Requirement: Contratos y consultas seguras de clientes

Las entradas Create y Update SHALL estar separadas de los modelos persistentes y SHALL rechazar con 422 `id`, `cliente_id` en el cuerpo de perfil y cualquier campo desconocido. El perfil SHALL obtenerse con precarga sin consultas implícitas al serializar. La API SHALL usar handlers asíncronos y una sesión por petición; los errores 409 SHALL NOT filtrar SQL, nombres internos ni trazas. Este change SHALL NOT incorporar autenticación, DELETE, modificación del perfil ni `GET /clientes/{id}/ventas`, reservado para C-05.

#### Scenario: Entradas desconocidas
- **WHEN** un alta incluye `id`, un perfil incluye `cliente_id` o cualquier entrada incluye otro campo no declarado
- **THEN** responde 422 sin persistir la petición

#### Scenario: Perfil precargado
- **WHEN** se consulta un cliente con perfil y otro sin él
- **THEN** ambos se serializan sin emitir consultas adicionales durante la lectura del objeto relacionado
