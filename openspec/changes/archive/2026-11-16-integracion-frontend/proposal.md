# Proposal

## Why

La consigna global reutiliza las pantallas del primer parcial y exige conectarlas a la API de la librería. El frontend actual funciona con `localStorage` y datos simulados; sin esta integración, el despliegue público no usaría PostgreSQL ni los contratos de FastAPI.

## What Changes

- Incorporar el frontend existente a `frontend/` con los HTML, CSS y JavaScript nativos, organizados bajo `public/`.
- Crear un cliente HTTP centralizado con base `/api`, manejo de errores del servidor y normalización de las respuestas de la API.
- Conectar el catálogo a `GET /libros/` con búsqueda por título, paginación, detalle y autores desde `GET /libros/{id}`; mostrar estados de carga, vacío, sin resultados y error.
- Conectar las altas a `POST /libros/` y `POST /clientes/`, cargando editoriales, géneros y autores desde la API; mostrar 201, 409 y 422.
- Conectar ventas a `POST /ventas/`, mostrando los importes devueltos por la API y conservando el borrador si la operación se rechaza.
- Conectar el historial a `GET /ventas/` y `GET /ventas/{id}` con paginación y detalle por venta.
- Agregar `frontend/Dockerfile`, `.dockerignore` y `default.conf.template` con Nginx y proxy `/api/` hacia `API_UPSTREAM`.
- Verificar localmente el frontend servido por Nginx contra el backend y documentar la publicación manual en EasyPanel.

## Capabilities

### New Capabilities

- `frontend-integration`: catálogo, altas, ventas e historial conectados a la API, con paginación, estados y errores.
- `frontend-container`: imagen Nginx del frontend con proxy `/api/` configurable por `API_UPSTREAM`.

### Modified Capabilities

Ninguna. Los contratos de la API y el contenedor del backend no cambian.

## Impact

Se agregan `frontend/public/`, `frontend/Dockerfile`, `frontend/.dockerignore`, `frontend/default.conf.template` y documentación de ejecución. No se modifica el backend, la base ni las dependencias Python. La publicación en EasyPanel queda como operación manual posterior; este change deja todo listo y probado localmente.
