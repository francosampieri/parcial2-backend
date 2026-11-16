# Imagen Docker y publicación de la API

## Despliegue real del parcial

- **URL pública:** `https://parcial2-api.maurodip.me/` (`/health/ready` respondió `{"estado":"listo"}` por HTTPS). El grupo confirmó que la cátedra autorizó usar esta VPS; no se confirmó una autorización específica para EasyPanel.
- **Fecha:** publicación comprobada el 12 de noviembre de 2026; actualización con el aviso D-07 y venta de verificación 3 a las `2026-11-13T02:17:58Z` (UTC). No se registró la hora exacta de la primera implementación.
- **Entrega:** el grupo confirmó el 16/11/2026 que `Parcial_Cap1a4_totones.zip` ya fue subido al campus. El archivo no se conserva en este repositorio y la hora exacta de la subida no quedó registrada.
- **Revalidación externa (16/11/2026):** `GET /health/ready` respondió 200 `{"estado":"listo"}`; `GET /libros/`, `GET /ventas/` y `GET /clientes/1/ventas` respondieron 200 con los datos del seed y ventas de total `77000.00`. No se creó una venta nueva para no alterar los datos publicados.
- **Construcción y ejecución reales:** EasyPanel construyó el `Dockerfile` de la rama `main` del repositorio GitHub `francosampieri/parcial2-backend` y ejecutó la imagen como servicio App `parcial2-api` dentro del proyecto `totones`. PostgreSQL es el servicio privado y persistente `parcial2-db` del mismo proyecto, con host interno `totones_parcial2-db:5432`. EasyPanel administra el contenedor y el reinicio; el usuario no ejecutó `docker build` ni `docker run` para el servicio publicado. Por eso no se presentan comandos de esos tipos como evidencia de la publicación real. Se ejecutó un `docker run --rm --network none` solamente para D-05.
- **Configuración:** `DATABASE_URL` con `postgresql+asyncpg` se cargó de forma privada en Entorno de EasyPanel y `SQL_ECHO=false`; el valor secreto no aparece en este archivo, la imagen ni el repositorio. La API escucha en el puerto interno `8000`; el proxy de EasyPanel ofrece HTTPS. El seed se ejecutó con `python -m app.demo_seed` en la consola de la App.
- **Actualización:** publicar el commit en GitHub, pulsar **Implementar** en `totones/parcial2-api`, comprobar `/health/ready` y, si EasyPanel restablece el modo de red que falla en esta VPS, ejecutar `docker service update --endpoint-mode dnsrr totones_parcial2-api`. La base permanece en su servicio propio, por lo que la venta 2 conservó el total `77000.00` tras recrear la API. El commit `0792fce` hizo visible el aviso D-07 en los logs y fue implementado así.
- **Límites conocidos:** no se comprobó la continuidad del dominio de `calculadora`; el ajuste `dnsrr` puede perderse en un nuevo despliegue de EasyPanel; no se capturó el estado explícito `healthy` ni el código HTTP 201 del POST de venta. La evidencia distingue estos puntos como pendientes y no los declara aprobados.

## Publicación manual del frontend (evaluación global)

El frontend se publicó como **`parcial2-frontend`** dentro del mismo proyecto `totones`, sin crear un cuarto proyecto ni tocar `parcial2-db`.

- **URL pública:** `https://parcial2.maurodip.me` (verificada el 16/11/2026).
- **Arranque observado:** logs de Nginx del 16/11/2026 a las 15:23:37 (hora del servidor).
- **Dominio:** `parcial2.maurodip.me`, puerto interno 80 y HTTPS.
- **Variable:** `API_UPSTREAM=totones_parcial2-api:8000`.
- **Proxy:** `/api/` hacia el backend interno; sin CORS.

La ejecución es manual en EasyPanel.

### Preparación del repositorio

El frontend vive en `frontend/` de este repositorio, con:

```text
frontend/
  Dockerfile
  .dockerignore
  default.conf.template
  public/
```

EasyPanel debe construir desde la rama `main` con **Build Path `/frontend`**, builder **Dockerfile** y ruta `Dockerfile`.

### Servicio frontend

1. En `totones`, elegir **New Service → App** y nombrarlo `parcial2-web`.
2. Source: repositorio `francosampieri/parcial2-backend`, rama `main`, Build Path `/frontend`.
3. Environment:

```text
API_UPSTREAM=totones_parcial2-api:8000
```

Sin `http://` y sin barra final. El nombre interno debe ser el que muestra EasyPanel para el servicio de la API.

4. Domains: host público del frontend (por ejemplo `parcial2.maurodip.me`), path `/`, puerto interno `80`, HTTPS activado.
5. Deploy.

El backend no se vuelve a desplegar para este cambio. La API puede conservar su dominio público durante la verificación; después se puede retirar si se quiere dejar sólo el acceso interno, como sugiere la guía global.

### Proxy y CORS

`default.conf.template` reenvía `/api/` a `http://${API_UPSTREAM}/`. La barra final elimina el prefijo: `/api/libros/` llega a FastAPI como `/libros/`. El navegador usa el mismo origen del frontend, así que no hace falta CORS.

### DNS y verificación

Si no existe un comodín `*.maurodip.me`, crear un registro **A** para el subdominio del frontend apuntando a la IP de la VPS. Luego:

```sh
curl -i https://parcial2.maurodip.me/
curl -i https://parcial2.maurodip.me/api/health/ready
curl -i https://parcial2.maurodip.me/api/libros/
```

Esperado: HTML 200, salud 200 `{"estado":"listo"}` y catálogo 200 con los datos del seed.

### Diagnóstico de 502

1. Comprobar la API directa: `curl -fsS https://parcial2-api.maurodip.me/health/ready`.
2. Revisar logs del servicio frontend.
3. Desde un contenedor de la VPS, probar el nombre interno:

```sh
wget -qO- http://totones_parcial2-api:8000/health/ready
```

4. Si el nombre VIP falla pero responde `tasks.totones_parcial2-api:8000`, usar ese valor temporalmente en `API_UPSTREAM`.
5. Reaplicar el ajuste ya conocido y revalidar:

```sh
docker service update --endpoint-mode dnsrr totones_parcial2-api
```

Ese ajuste puede perderse en cada redeploy de la API; hay que comprobarlo después de actualizar.

### Actualización y vuelta atrás

- **Actualizar:** push a `main`, Deploy del servicio frontend y, si cambió la API, redeploy del backend; revalidar `/api/health/ready` y el `dnsrr` si reaparece el 502.
- **Volver atrás:** redeploy del commit anterior del frontend o eliminar sólo `parcial2-web`. La API y la base PostgreSQL no se tocan.

La evidencia funcional local de G-01 a G-07 está en [`docs/evidencia/G-global.md`](docs/evidencia/G-global.md). La evidencia pública se completa después de ejecutar estos pasos manuales.

La [evidencia de VPS](docs/evidencia/C08-vps-parcial.md) detalla comandos, resultados observados y límites de verificación. Los comandos `docker build` y `docker run` siguientes son **ejemplos para una instalación directa**, no el método EasyPanel efectivamente usado. La consigna solicita explícitamente `docker run`; esta diferencia queda declarada para la corrección.

## Qué se ejecuta

Una **imagen** es la plantilla construida desde `Dockerfile`. Un **contenedor** es una instancia de esa imagen. La imagen contiene Python, las dependencias y `app/`; PostgreSQL y sus datos están fuera. Por eso se puede destruir y recrear sólo el contenedor de la API sin perder los registros, siempre que ambos arranques apunten a la misma base externa.

Docker construye por capas. `requirements.txt` se copia e instala antes de `app/`: un cambio de código no obliga a reinstalar dependencias si la capa de requisitos sigue en caché. `pip --no-cache-dir` evita guardar su caché en la imagen. `.dockerignore` reduce el contexto a `requirements.txt` y `app/` y excluye archivos de entorno, Git, entornos virtuales y cachés. Nunca incorporar la URL real de la base al Dockerfile ni publicar el archivo privado de variables.

## Preparar parámetros y conexión

Ejemplo para un shell Linux. El archivo de variables debe estar **fuera del repositorio**, con acceso limitado al operador. La base y el usuario PostgreSQL ya deben existir y permitir crear tablas. No usar la base de otro proyecto para pruebas.

```sh
IMAGE=totones-api:local
CONTAINER=totones-api
HOST_BIND=127.0.0.1
HOST_PORT=8081
DATABASE_ENV_FILE=/ruta/privada/totones-api.env
```

Contenido esperado del archivo privado, con valores reales colocados **sólo** en el servidor o equipo de prueba:

```dotenv
DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@HOST_DB:5432/BASE_PROPIA
SQL_ECHO=false
```

En Linux, se puede limitar su lectura con `chmod 600 "$DATABASE_ENV_FILE"`. La sintaxis de la URL corresponde al driver asyncpg; si la contraseña tiene caracteres reservados, codificarlos para URL. El host de PostgreSQL debe poder alcanzarse **desde el contenedor**. `localhost` en `DATABASE_URL` designa el propio contenedor, no la máquina anfitriona. En Docker Desktop, `host.docker.internal` puede conectar con un servicio del host si éste acepta la conexión; en Linux hay que verificar la dirección de red, `listen_addresses`, reglas de acceso y firewall antes de usar un hostname concreto. La red hacia PostgreSQL es independiente de publicar el puerto HTTP.

## Construir y ejecutar

Desde la raíz del proyecto, con un daemon Docker Linux disponible:

```sh
docker build -t "$IMAGE" .
docker pull python:3.12-alpine
docker image inspect python:3.12-alpine --format '{{.Size}}'
docker image inspect "$IMAGE" --format '{{.Config.User}} {{json .Config.Healthcheck}}'
docker run -d --name "$CONTAINER" \
  --restart unless-stopped \
  --env-file "$DATABASE_ENV_FILE" \
  -p "${HOST_BIND}:${HOST_PORT}:8000" \
  "$IMAGE"
```

`docker image inspect` devuelve bytes para la **imagen base**; el requisito menor a 100 MB se comprueba sobre `python:3.12-alpine`, no sobre la imagen final que también contiene dependencias. Medirla después del build porque la etiqueta puede cambiar. Para ver MiB: dividir el valor por 1 048 576. La opción `-p` conecta un puerto del host elegido con el 8000 interno, donde Uvicorn escucha en `0.0.0.0`. `HOST_BIND=127.0.0.1` limita la exposición a la propia máquina, apropiado si luego hay un proxy local; decidir el bind real en C-08 según la red existente. `--restart unless-stopped` vuelve a iniciar el proceso tras una caída o reinicio del host, salvo detención manual; no repara una URL de base errónea ni una base caída.

## Comprobar salud y diagnóstico

```sh
docker ps --filter "name=$CONTAINER"
docker inspect "$CONTAINER" --format '{{.State.Health.Status}}'
docker exec "$CONTAINER" id -u
curl -fsS "http://${HOST_BIND}:${HOST_PORT}/health/ready"
docker logs --tail 100 "$CONTAINER"
```

El UID debe ser distinto de cero. El `HEALTHCHECK` de la imagen consulta `http://127.0.0.1:8000/health/ready` **dentro** del contenedor. Sólo HTTP 200 indica `healthy`; esa ruta ejecuta `SELECT 1` contra PostgreSQL. Si la base deja de responder después de un inicio correcto, Docker pasa a `unhealthy` tras sus intervalos; el proceso puede seguir vivo. Si falta `DATABASE_URL` o la base es inaccesible durante el arranque, la API falla y no queda sirviendo. Revisar `docker logs` y `docker inspect` para distinguir esos casos. En una prueba de fallos usar `--restart no` para evitar un bucle de reinicios.

## Seed y datos persistidos

El seed es explícito; no se ejecuta al arrancar. Con la API y su base ya disponibles:

```sh
docker exec "$CONTAINER" python -m app.demo_seed
```

El comando muestra IDs reales y crea sólo registros faltantes; no sustituirlos por IDs inventados en las peticiones de prueba. Para verificar persistencia en un **entorno de prueba aislado**, detener y eliminar únicamente este contenedor y volver a usar la misma URL de base:

```sh
docker stop "$CONTAINER"
docker rm "$CONTAINER"
docker run -d --name "$CONTAINER" \
  --restart unless-stopped \
  --env-file "$DATABASE_ENV_FILE" \
  -p "${HOST_BIND}:${HOST_PORT}:8000" \
  "$IMAGE"
curl -fsS "http://${HOST_BIND}:${HOST_PORT}/health/ready"
```

Consultar después un libro o cliente creado por el seed con su ID real. El primer startup crea las tablas faltantes, pero `create_all` no migra columnas existentes ni borra filas.

## Actualización de la aplicación

Construir una nueva etiqueta a partir del código revisado y comprobarla primero en un ambiente de prueba. Para actualizar el servicio de este parcial, detener y eliminar **sólo** su contenedor, conservar el archivo privado y la base, y ejecutar `docker run` con la nueva etiqueta y los mismos parámetros. Registrar la etiqueta anterior para poder volver a ella si la nueva versión falla. No detener el contenedor del otro proyecto ni modificar su PostgreSQL sin inspeccionar la VPS en C-08.

## Registro de verificación

Estas casillas requieren una ejecución real; los archivos por sí solos no prueban el resultado.

| Comprobación | Resultado / evidencia |
|---|---|
| `docker build`, base menor a 100 MB, usuario y healthcheck de imagen | Verificado localmente; ver [evidencia C-07](docs/evidencia/C07-local.md) |
| Contenedor con PostgreSQL aislado: `healthy`, ready 200, puerto y tablas | Verificado localmente; ver evidencia C-07 |
| Sin URL, DB inaccesible al inicio y caída posterior: logs/estado | Verificado localmente; ver evidencia C-07 |
| Seed por `docker exec`, recreación y filas conservadas | Verificado localmente; ver evidencia C-07 |
| URL pública real de VPS | `https://parcial2-api.maurodip.me/health/ready` respondió `{"estado":"listo"}` por HTTPS; ver [evidencia C-08](docs/evidencia/C08-vps-parcial.md) |
| Fecha, comandos y capturas o salidas sanitizadas de VPS | Evidencia parcial de C-08 registrada; D-07 se verificó en logs con venta 3 tras el commit 0792fce; recuperación de calculadora sigue pendiente |

No presentar resultados locales como evidencia de VPS. Antes de compartir logs o capturas, quitar URL de conexión, usuarios, contraseñas, direcciones privadas y otros secretos.

## Empaquetado de la evaluación global

Para armar el ZIP con la estructura pedida por la cátedra:

```sh
.venv/bin/python scripts/empaquetar_global.py
```

Genera `dist/Parcial_Global_totones.zip` con `frontend/`, `backend/`, `README.md`,
`DEPLOY.md` y `evidencia/`. El script excluye `.env`, `.venv`, `__pycache__`,
`.git`, `tmp/` y dependencias instaladas. Volver a ejecutarlo después de publicar
el frontend para que la URL y la fecha queden en la entrega.

