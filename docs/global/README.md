# El Tintero — Librería web integrada

Trabajo Práctico de **Programación III**, comisión **2PRO1**, grupo **totones**.

Integrantes: Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria.

Aplicación de librería con frontend HTML/CSS/JavaScript nativo, API FastAPI y
PostgreSQL. Las pantallas del primer parcial consultan la API real: catálogo,
altas de libros y clientes, venta con renglones e historial con precios históricos.

## Estructura de la entrega

```text
Parcial_Global_totones/
  frontend/
    Dockerfile
    .dockerignore
    default.conf.template
    env.example
    public/
  backend/
    Dockerfile
    .dockerignore
    requirements.txt
    requirements-dev.txt
    env.example
    app/
    tests/
    test/
  README.md
  DEPLOY.md
  evidencia/
```

## Arquitectura

```text
Navegador
  → Nginx del frontend (HTTPS)
    → /api/ (proxy interno)
      → FastAPI
        → PostgreSQL
```

El navegador usa el mismo origen del frontend; Nginx elimina el prefijo `/api/`
y reenvía al backend. No se requiere CORS.

## Ejecutar localmente

Requisitos: Python 3.12+, PostgreSQL 16+ y Docker.

### Backend

```sh
cd backend
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp env.example .env
```

Editar `.env` con una base PostgreSQL propia:

```dotenv
DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@127.0.0.1:5432/BASE_PROPIA
SQL_ECHO=false
```

Levantar la API y cargar los datos de ejemplo:

```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
python -m app.demo_seed
```

Comprobar:

```sh
curl -fsS http://127.0.0.1:8000/health/ready
```

### Frontend

En otra terminal:

```sh
cd frontend
docker build -t libreria-frontend .
docker run --rm --name libreria-frontend \
  -p 127.0.0.1:8080:80 \
  --add-host=host.docker.internal:host-gateway \
  -e API_UPSTREAM=host.docker.internal:8000 \
  libreria-frontend
```

Abrir `http://127.0.0.1:8080`.

El backend debe escuchar en `0.0.0.0:8000` para que el contenedor lo alcance con
`host.docker.internal`.

## Variables de entorno

| Componente | Variable | Uso |
|---|---|---|
| Backend | `DATABASE_URL` | URL de PostgreSQL con driver `postgresql+asyncpg`. Obligatoria. |
| Backend | `SQL_ECHO` | `true`/`false`; diagnóstico SQL. En producción, `false`. |
| Frontend | `API_UPSTREAM` | Host y puerto internos del backend, sin `http://` ni barra final. |

Los archivos `backend/env.example` y `frontend/env.example` contienen los nombres
y valores de muestra; no incluyen credenciales reales.

## Operaciones principales

- Catálogo: búsqueda por título, paginación, detalle y autores.
- Libros: alta con editorial, género opcional, stock y autorías con rol/orden.
- Clientes: alta y consulta individual por ID.
- Ventas: cliente, renglones, precios copiados y total calculado por el servidor.
- Historial: listado paginado y detalle con importes históricos.

La API no expone listados generales de autores ni clientes; el frontend los busca
por ID con `GET /api/autores/{id}` y `GET /api/clientes/{id}`.

## Evidencia

Los registros están en [`evidencia/`](evidencia/). El caso global y su estado
público se documentan en `evidencia/G-global.md`.

## Publicación

La URL pública y los pasos manuales de EasyPanel se registran en
[`DEPLOY.md`](DEPLOY.md).
