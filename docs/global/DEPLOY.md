# Despliegue — Librería web integrada

Grupo **totones** — Programación III, 2PRO1.

## Datos de la publicación

- **URL pública del frontend:** `https://parcial2.maurodip.me` (verificada el 16/11/2026).
- **API interna:** `http://totones_parcial2-api:8000`.
- **Fecha y hora del despliegue:** 16/11/2026; los logs de Nginx del servicio `parcial2-frontend` muestran el arranque a las 15:23:37 (hora del servidor).
- **Proyecto EasyPanel:** `totones`.
- **Servicios:** `parcial2-frontend` (frontend), `parcial2-api` (API), `parcial2-db` (PostgreSQL).

Verificación inicial observada: `GET /` → 200 con el HTML de El Tintero;
`GET /api/health/ready` → 200 `{"estado":"listo"}`; `GET /api/libros/` → 200
con los datos del seed. La evidencia funcional completa se registra en
`evidencia/G-global.md`.

No se incluyen contraseñas, cadenas de conexión privadas ni valores reales de
`DATABASE_URL`.

## Arquitectura publicada

```text
Navegador
  → https://<dominio-frontend>
    → Nginx (puerto interno 80)
      → /api/ → http://totones_parcial2-api:8000/
        → PostgreSQL privado totones_parcial2-db:5432
```

El frontend y la API se comunican por la red interna del proyecto. El navegador
sólo habla con el dominio del frontend; no se necesita CORS.

## Build paths

En el repositorio de despliegue (backend en la raíz):

| Servicio | Repositorio | Build Path | Dockerfile |
|---|---|---|---|
| `parcial2-api` | `francosampieri/parcial2-backend` | `/` | `Dockerfile` |
| `parcial2-web` | `francosampieri/parcial2-backend` | `/frontend` | `Dockerfile` |

Si se despliega desde una copia con ambas carpetas (`frontend/` y `backend/`),
usar `/backend` y `/frontend` respectivamente.

## Variables

### Backend

```dotenv
DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@HOST:5432/BASE
SQL_ECHO=false
```

Cargar `DATABASE_URL` en el entorno privado del servicio API. No versionarla.

### Frontend

```text
API_UPSTREAM=totones_parcial2-api:8000
```

Sin `http://` y sin barra final. El nombre interno debe ser el que muestra
EasyPanel para el servicio API.

## Configuración de Nginx

`frontend/default.conf.template`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://${API_UPSTREAM}/;
    }
}
```

La barra final de `proxy_pass` elimina `/api`: `/api/libros/` llega a FastAPI
como `/libros/`.

## Pasos de publicación

1. Crear el dominio del frontend en el DNS y apuntarlo a la VPS.
2. En EasyPanel, dentro de `totones`, crear **New Service → App** llamado
   `parcial2-web`.
3. Source: repositorio, rama `main`, Build Path `/frontend`.
4. Builder: Dockerfile; ruta `Dockerfile`.
5. Environment: `API_UPSTREAM=totones_parcial2-api:8000`.
6. Domains: host público, path `/`, protocolo interno HTTP, puerto 80, HTTPS.
7. Deploy.
8. Verificar `/api/health/ready` y el catálogo.

El backend no cambia para esta publicación. La base `parcial2-db` permanece.

## Verificación externa

```sh
curl -i https://parcial2.maurodip.me/
curl -i https://parcial2.maurodip.me/api/health/ready
curl -i https://parcial2.maurodip.me/api/libros/
curl -i https://parcial2.maurodip.me/api/ventas/
```

Esperado: HTML 200, salud 200 `{"estado":"listo"}`, catálogo y ventas 200.

## Diagnóstico de 502

1. Verificar la API directa:

```sh
curl -fsS https://parcial2-api.maurodip.me/health/ready
```

2. Revisar los logs del servicio `parcial2-web`.
3. Desde un contenedor del frontend:

```sh
wget -qO- http://totones_parcial2-api:8000/health/ready
wget -qO- http://tasks.totones_parcial2-api:8000/health/ready
```

4. Si el nombre normal falla y `tasks.` responde, usar
   `API_UPSTREAM=tasks.totones_parcial2-api:8000` o reaplicar:

```sh
docker service update --endpoint-mode dnsrr totones_parcial2-api
```

Ese ajuste puede perderse en un nuevo despliegue de la API; revalidar después de
cada actualización.

## Actualización y vuelta atrás

- **Actualizar:** push a `main`; Deploy del frontend y, si cambió la API, del
  backend. Verificar salud, catálogo y una venta.
- **Volver atrás:** redeploy del commit anterior del frontend o eliminar sólo
  `parcial2-web`. La API y PostgreSQL no se tocan.
- **Persistencia:** la base está fuera del contenedor; recrear la API no borra
  las ventas.

## Casos G

La evidencia se registra en `evidencia/G-global.md`:

- G-01 Catálogo, búsqueda, paginación y detalle.
- G-02 Alta de libro y 409 por ISBN repetido.
- G-03 Alta de cliente, consulta por ID y 409 por email repetido.
- G-04 Venta con dos renglones, 201 y detalle tras recargar.
- G-05 Precio histórico tras `PATCH /libros/{id}`.
- G-06 Rechazos 409/422 y conservación del historial.
- G-07 Build del frontend, HTTPS, salud y persistencia tras redesplegar.
