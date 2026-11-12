# Tasks

## 1. Imagen y contexto de construcción

- [x] 1.1 Incorporar `.dockerignore` para excluir `.env`, `.venv`, `.git`, `__pycache__`, cachés y artefactos locales; verificar con una inspección concreta del contexto/layers que los archivos sensibles no viajan ni quedan en la imagen.
- [x] 1.2 Crear `Dockerfile` con `python:3.12-alpine`, instalación de `requirements.txt` mediante `pip --no-cache-dir` antes de copiar `app/`, usuario no root, Uvicorn en `0.0.0.0:8000` y HEALTHCHECK ready en `127.0.0.1`; verificar `docker build`, el tamaño real de la **base** (<100 MB) y que el usuario/configuración del artefacto coinciden con el contrato. Corregir sólo incompatibilidades de Alpine demostradas por el build; si se modifica código o dependencias, ejecutar la suite existente y contrastar con su línea base.

## 2. Ejecución aislada y guía

- [x] 2.1 Iniciar la imagen con `docker run` y un env-file de prueba contra PostgreSQL aislado y alcanzable desde el contenedor; verificar `healthy`, `/health/ready` 200, servicio por puerto host elegido, usuario efectivo no root y creación de tablas sobre base vacía. Registrar comandos/salidas sanitizados locales sin etiquetarlos como evidencia D de VPS.
- [x] 2.2 Verificar el fallo de startup sin `DATABASE_URL` y con DB inaccesible, y el estado `unhealthy` si una DB de prueba previamente disponible cae; observar logs/estado del contenedor y evitar reinicios permanentes durante estas comprobaciones.
- [x] 2.3 Ejecutar `python -m app.demo_seed` mediante `docker exec`, recrear sólo el contenedor de prueba con la misma DB y comprobar que siguen presentes las filas; documentar resultados locales sanitizados.
- [x] 2.4 Crear `DEPLOY.md` con build/run parametrizados (puerto, env-file, DB externa, `--restart unless-stopped`), seed, diagnóstico, actualización y campos de URL/fecha/evidencias reales pendientes; verificar que los comandos son coherentes con la imagen y no contienen secretos. Explicar imagen/contenedor, caché de capas, puertos, red hacia PostgreSQL, healthcheck y restart. Si el daemon sigue inaccesible, dejar pendientes las verificaciones Docker y reportar la limitación.
