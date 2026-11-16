# frontend-container Specification

## Purpose

Servir el frontend estático y reenviar las llamadas `/api/` al backend interno mediante Nginx, sin CORS y con la URL del backend configurable por entorno.

## Requirements

### Requirement: Imagen Nginx del frontend

La imagen SHALL usar Nginx, copiar `public/` al directorio servido y exponer el puerto 80. La configuración SHALL conservar las rutas relativas de HTML, CSS y JavaScript y SHALL servir las páginas del frontend.

#### Scenario: Página principal
- **WHEN** un navegador solicita `/` al contenedor
- **THEN** Nginx devuelve el `index.html` del frontend

#### Scenario: Recursos estáticos
- **WHEN** el navegador solicita `css/styles.css` o un archivo de `js/`
- **THEN** Nginx devuelve el recurso con su tipo correcto

### Requirement: Proxy `/api/` configurable

La plantilla de Nginx SHALL reenviar `/api/` a `http://${API_UPSTREAM}/`, eliminando el prefijo `/api` y conservando la ruta restante. `API_UPSTREAM` SHALL recibirse por variable de entorno, sin `http://` y sin barra final. El contenedor SHALL NOT incorporar credenciales ni la URL privada de PostgreSQL.

#### Scenario: Salud a través del proxy
- **WHEN** el contenedor se inicia con un upstream válido y se consulta `/api/health/ready`
- **THEN** Nginx reenvía la petición a `/health/ready` del backend y devuelve su estado

#### Scenario: Upstream ausente o incorrecto
- **WHEN** `API_UPSTREAM` no está definido o el backend no responde
- **THEN** el frontend sigue sirviendo sus archivos y las llamadas a `/api/` fallan con un error controlado, sin exponer configuración privada

### Requirement: Verificación local del contenedor

La entrega SHALL documentar la construcción y ejecución local del contenedor del frontend junto al backend, con una variable de ejemplo y un comando de comprobación de `/api/health/ready`. La verificación SHALL usar datos ficticios y SHALL NOT requerir la VPS.

#### Scenario: Prueba local completa
- **WHEN** se ejecutan el backend y el contenedor del frontend en la misma máquina
- **THEN** la URL local permite consultar el catálogo y registrar una venta contra la API local

#### Scenario: Sin CORS
- **WHEN** el navegador carga el frontend desde el contenedor Nginx
- **THEN** las peticiones a `/api/` son del mismo origen y no requieren cabeceras CORS del backend
