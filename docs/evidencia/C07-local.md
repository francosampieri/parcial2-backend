# C-07 — verificación local de la imagen

Fecha: 2026-11-12. Ejecución en Docker Desktop Linux 29.8.2 sobre una red Docker privada de prueba. Esta evidencia corresponde al equipo local; **no** demuestra publicación ni disponibilidad en la VPS (C-08).

## Imagen y contexto

- `docker build --progress=plain -t totones-api:c07-local .`: correcto. `pip install --no-cache-dir -r requirements.txt` instaló las versiones fijadas sobre Alpine sin compilar ni modificar dependencias. La copia de `requirements.txt` precede a la de `app/` en el historial de capas.
- La base `python:3.12-alpine` se descargó y midió por separado: **74.098.022 bytes** (<100 MB). La imagen final midió **258.357.932 bytes**; el límite de la consigna corresponde sólo a la base.
- `docker image inspect`: `Config.User=api`, comando `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`, healthcheck en `127.0.0.1:8000/health/ready`. La configuración de la imagen no contiene `DATABASE_URL`.
- La inspección del sistema de archivos de la imagen mostró sólo `requirements.txt` y `app/` dentro de `/srv/api`. Para comprobar el filtro, se crearon temporalmente marcadores **ficticios** `.env.c07-context-check` en la raíz y en `app/`, se reconstruyó con caché y se comprobó que ambos estaban ausentes. Los marcadores se eliminaron al terminar. No se introdujeron secretos reales.

## Ejecución y datos

Se creó exclusivamente para esta prueba un PostgreSQL 17 Alpine en otro contenedor, con red y volumen privados; el archivo de variables quedó en `tmp/`, ignorado por Git. PostgreSQL no formó parte de la imagen de la API ni publicó su puerto al host.

| Prueba | Resultado observado |
|---|---|
| API en puerto host `127.0.0.1:18081` conectado al 8000 del contenedor | HTTP 200 en `/health/ready`; estado Docker `healthy` |
| Usuario efectivo `docker exec ... id -u` | UID 100, distinto de root |
| Arranque sobre base vacía | Nueve tablas creadas |
| Arranque sin `DATABASE_URL`, `--restart no` | Proceso detenido, exit 3; error de configuración en logs |
| Arranque con DB inalcanzable, `--restart no` | Proceso detenido, exit 3; error de base no disponible en logs |
| Caída posterior de PostgreSQL de prueba | `/health/ready` respondió 503; API siguió `running` y Docker pasó a `unhealthy` tras fallos del healthcheck |
| Recuperación de PostgreSQL de prueba | Docker volvió a `healthy` |
| `docker exec codex-c07-api python -m app.demo_seed` | Se generaron editorial, género, dos autores, cuatro libros y un cliente; IDs obtenidos del seed |
| Recreación de **sólo** la API con la misma base | `healthy`, ready 200 y cuatro filas en `libro` conservadas |

Las comprobaciones de C-08 sobre URL pública, fecha, configuración y evidencias de la VPS siguen pendientes. No se imprimieron contraseñas ni URL reales en este registro.
