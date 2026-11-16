# El Tintero — Frontend integrado

Frontend estático de la librería para la **Evaluación Global** de Programación III.
Reutiliza las pantallas del primer parcial y las conecta a la API FastAPI del TP de
catálogo, clientes y ventas.

## Estructura

```text
frontend/
  Dockerfile
  .dockerignore
  default.conf.template
  public/
    index.html
    catalogo.html
    libros.html
    clientes.html
    ventas.html
    historial.html
    css/styles.css
    js/api.js
    js/formato.js
    js/catalogo.js
    js/altas.js
    js/ventas.js
    js/historial.js
```

`api.js` centraliza `fetch` con la base `/api`. `formato.js` contiene el formato de
importes y fechas. El resto de los módulos usa esos helpers.

## Rutas de la API utilizadas

| Pantalla | Rutas |
|---|---|
| Catálogo | `GET /api/libros/`, `GET /api/libros/{id}` |
| Libros | `GET /api/editoriales/`, `GET /api/generos/`, `GET /api/autores/{id}`, `POST /api/libros/` |
| Clientes | `POST /api/clientes/`, `GET /api/clientes/{id}` |
| Ventas | `GET /api/libros/`, `GET /api/clientes/{id}`, `POST /api/ventas/` |
| Historial | `GET /api/ventas/`, `GET /api/ventas/{id}` |

La API no expone listados de autores ni de clientes. Por eso los formularios piden
un ID, consultan el recurso individual y muestran el nombre antes de usarlo. Los
clientes creados o consultados se mantienen en una tabla de sesión.

## Ejecución local

1. Levantá el backend con una base PostgreSQL propia y cargá los datos de ejemplo:

```sh
DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@127.0.0.1:5432/BASE_PROPIA \
  uvicorn app.main:app --host 0.0.0.0 --port 8000

DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@127.0.0.1:5432/BASE_PROPIA \
  python -m app.demo_seed
```

2. Construí y ejecutá el frontend:

```sh
docker build -t libreria-frontend .
docker run --rm --name libreria-frontend \
  -p 127.0.0.1:8080:80 \
  --add-host=host.docker.internal:host-gateway \
  -e API_UPSTREAM=host.docker.internal:8000 \
  libreria-frontend
```

3. Abrí `http://127.0.0.1:8080` y comprobá:

```sh
curl -fsS http://127.0.0.1:8080/api/health/ready
```

Con el proxy de Nginx, el navegador y la API comparten origen: **no se necesita CORS**.

En Linux, si el backend escucha sólo en `127.0.0.1`, ejecutalo con `--host 0.0.0.0`
para que el contenedor lo alcance mediante `host.docker.internal`.

## Variables

| Variable | Uso |
|---|---|
| `API_UPSTREAM` | Host y puerto internos del backend, por ejemplo `host.docker.internal:8000` o `totones_parcial2-api:8000`. Sin `http://` y sin barra final. |

El contenedor no recibe `DATABASE_URL` ni credenciales de PostgreSQL; esas variables
pertenecen al backend.

## Publicación

La publicación manual en EasyPanel, el dominio, el Build Path `/frontend` y el
diagnóstico de un 502 están documentados en [`../DEPLOY.md`](../DEPLOY.md).
