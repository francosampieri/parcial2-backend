# Imagen Docker y publicación de la API

Esta guía prepara la imagen de C-07. Los valores reales de la VPS y las evidencias de publicación corresponden a C-08: primero hay que inspeccionar el servidor, su PostgreSQL y el proyecto que ya funciona allí. Los comandos siguientes son ejemplos parametrizados para una terminal Linux; reemplazar cada ruta y puerto por los del entorno elegido.

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
| URL pública real de VPS | Pendiente de C-08 |
| Fecha, comandos y capturas o salidas sanitizadas de VPS | Pendiente de C-08 |

No presentar resultados locales como evidencia de VPS. Antes de compartir logs o capturas, quitar URL de conexión, usuarios, contraseñas, direcciones privadas y otros secretos.
