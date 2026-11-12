# health-monitoring Specification

## Purpose

Distinguir mediante HTTP si el proceso de la API sigue funcionando y si su dependencia PostgreSQL está disponible para atender operaciones de persistencia.

## Requirements

### Requirement: Liveness independiente de PostgreSQL

`GET /health/live` SHALL responder HTTP 200 con JSON `{"estado":"vivo"}` sin consultar PostgreSQL ni crear una sesión de base de datos para esa operación. Este contrato aplica después de un startup exitoso; SHALL NOT permitir eludir el fallo de startup por falta de configuración o conexión.

#### Scenario: Proceso iniciado y base disponible
- **WHEN** se consulta `/health/live` después de un startup correcto
- **THEN** responde 200 y `{"estado":"vivo"}` sin ejecutar SQL

#### Scenario: Caída posterior de la base
- **WHEN** PostgreSQL deja de estar disponible después de un startup correcto y se consulta `/health/live`
- **THEN** mantiene la respuesta 200 y `{"estado":"vivo"}` sin intentar conectarse a PostgreSQL

### Requirement: Readiness comprueba la base en cada petición

`GET /health/ready` SHALL ejecutar `SELECT 1` contra PostgreSQL en cada petición y SHALL responder HTTP 200 con JSON `{"estado":"listo"}` sólo si esa comprobación termina correctamente. Si después de un startup exitoso falla la obtención de conexión o la consulta por indisponibilidad de PostgreSQL, SHALL responder HTTP 503 con JSON `{"detail":"Base de datos no disponible"}` sin SQL, trazas, direcciones ni detalles del controlador. Una petición posterior con la base recuperada SHALL volver a responder 200.

#### Scenario: Base disponible
- **WHEN** se consulta `/health/ready` con PostgreSQL accesible
- **THEN** ejecuta `SELECT 1` y devuelve 200 con `{"estado":"listo"}`

#### Scenario: No se puede obtener conexión
- **WHEN** PostgreSQL queda inaccesible después del startup y una petición ready no logra conectarse
- **THEN** devuelve 503 con `{"detail":"Base de datos no disponible"}` y libera los recursos de la petición

#### Scenario: Falla la consulta de comprobación
- **WHEN** se obtiene conexión pero `SELECT 1` falla por indisponibilidad de PostgreSQL
- **THEN** devuelve el mismo 503 propio sin exponer detalles internos

#### Scenario: Base recuperada
- **WHEN** después de una respuesta 503 se recupera PostgreSQL y se vuelve a consultar ready
- **THEN** realiza una comprobación nueva y devuelve 200 con `{"estado":"listo"}`
