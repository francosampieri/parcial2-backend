# Proposal

## Why

La API y los datos de demostración ya están preparados; falta empaquetarla de forma reproducible para ejecutarla como contenedor y, después, publicarla en la VPS. Este change resuelve el empaquetado y su comprobación local sin intervenir el servidor compartido.

## What Changes

- Incorporar una imagen basada en `python:3.12-alpine`, con dependencias instaladas antes de copiar el código y ejecución con usuario sin privilegios.
- Excluir secretos y archivos locales del contexto Docker; recibir la configuración de PostgreSQL mediante variables externas.
- Iniciar Uvicorn en `0.0.0.0:8000` y declarar una comprobación Docker sobre `/health/ready` en `127.0.0.1`.
- Documentar `docker build`, `docker run` sin Compose, seed dentro del contenedor y actualización/recreación con parámetros, en `DEPLOY.md`.
- Comprobar localmente los contratos del contenedor con PostgreSQL aislado cuando haya un daemon Docker accesible. La medición menor a 100 MB corresponde a la imagen **base**, no a la imagen final; las evidencias D de VPS quedan para C-08.

## Capabilities

### New Capabilities

- `container-image`: empaquetado seguro y ejecución reproducible de la API en un contenedor conectado a PostgreSQL externo.

### Modified Capabilities

Ninguna: se reutilizan sin cambiar los contratos existentes de configuración, arranque y salud.

## Impact

Nuevos `Dockerfile`, `.dockerignore` y `DEPLOY.md`; posible ajuste menor de documentación o dependencias sólo si el build de Alpine lo exige. No cambia la API HTTP ni se modifica la VPS, su base de datos o el otro proyecto. C-08 completará los datos reales de publicación y la evidencia del servidor.
