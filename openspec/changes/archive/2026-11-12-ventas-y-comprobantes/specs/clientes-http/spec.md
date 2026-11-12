# Spec Delta

## MODIFIED Requirements

### Requirement: Contratos y consultas seguras de clientes

Las entradas Create y Update SHALL estar separadas de los modelos persistentes y SHALL rechazar con 422 `id`, `cliente_id` en el cuerpo de perfil y cualquier campo desconocido. El perfil SHALL obtenerse con precarga sin consultas implícitas al serializar. La API SHALL usar handlers asíncronos y una sesión por petición; los errores 409 SHALL NOT filtrar SQL, nombres internos ni trazas. Las operaciones de este capability SHALL NOT incluir autenticación, DELETE ni modificación del perfil. La consulta `GET /clientes/{id}/ventas` se especifica en `ventas-http`.

#### Scenario: Entradas desconocidas
- **WHEN** un alta incluye `id`, un perfil incluye `cliente_id` o cualquier entrada incluye otro campo no declarado
- **THEN** responde 422 sin persistir la petición

#### Scenario: Perfil precargado
- **WHEN** se consulta un cliente con perfil y otro sin él
- **THEN** ambos se serializan sin emitir consultas adicionales durante la lectura del objeto relacionado
