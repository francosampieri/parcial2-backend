# Design

## Context

Ver `proposal.md` para la motivación y `specs/container-image/spec.md` para el contrato. La API existente usa `app.main:app`, necesita `DATABASE_URL=postgresql+asyncpg://...`, crea tablas faltantes al arrancar, ofrece `/health/ready` y ejecuta el seed mediante `python -m app.demo_seed`. No existe aún Dockerfile. El daemon de Docker Desktop no está disponible en este entorno al proponer C-07, por lo que todavía no hay medición ni build real.

## Goals / Non-Goals

**Goals:**
- Un artefacto de contenedor reproducible con instalación compatible con Alpine, usuario no root y configuración inyectada en ejecución.
- Una guía parametrizada que permita probar y luego revisar el despliegue sin suponer datos de la VPS.
- Verificación local de los comportamientos nuevos en un entorno aislado cuando se disponga de Docker.

**Non-Goals:**
- Publicar en la VPS, cambiar su red, base, proxy o firewall, o completar evidencias D reales; corresponde a C-08.
- Añadir Compose, PostgreSQL a la imagen, migraciones o un seed automático.

## Decisions

1. **Una imagen de aplicación y PostgreSQL fuera de ella.** El Dockerfile partirá de `python:3.12-alpine`, instalará `requirements.txt` con `pip --no-cache-dir` en una capa anterior a copiar `app/` y luego declarará `USER` no root. Esa separación permite reutilizar la capa de dependencias al cambiar sólo código. Se verificará el build con las versiones fijadas, incluidas las dependencias nativas de `asyncpg`, `pydantic-core`, `greenlet`, `httptools` y `uvloop`; sólo se agregarán paquetes del sistema si un error concreto lo demuestra. Se descarta incluir PostgreSQL o una alternativa SQLite porque cambiaría la arquitectura y la persistencia exigidas.

2. **Configuración externa.** `.dockerignore` excluirá `.env`, `.venv`, `.git`, cachés y artefactos locales; Dockerfile sólo copiará archivos necesarios para ejecutar la API. `docker run --env-file <ARCHIVO>` inyectará `DATABASE_URL` y, opcionalmente, `SQL_ECHO=false`. El archivo real permanecerá fuera del repositorio. La dirección de DB deberá ser alcanzable desde el contenedor: `localhost` dentro de éste es el propio contenedor, no el host. La guía explicará la elección de red para el entorno local y dejará la configuración del host Linux sujeta a inspección en C-08.

3. **Proceso y salud.** Uvicorn escuchará en `0.0.0.0:8000`; `-p <PUERTO_HOST>:8000` decidirá la exposición sin modificar la imagen. `HEALTHCHECK` consultará con Python estándar `urllib` el IPv4 literal `127.0.0.1` y verificará HTTP 200, evitando instalar `curl`. Se utilizarán intervalos y plazos acotados para no marcar fallido un arranque normal. La ruta ready comprueba PostgreSQL; Docker señala `unhealthy` si la DB falla después del startup, mientras que el arranque existente detiene la API si no hay URL o DB.

4. **Ejecución y actualización documentadas.** `DEPLOY.md` incluirá build, run con `--restart unless-stopped`, comprobación con `docker ps`/logs/HTTP, seed mediante `docker exec`, reemplazo sólo del contenedor de este parcial y verificación de datos persistidos. Todos los nombres de imagen, contenedor, puerto, ruta de env-file, host y URL reales serán parámetros o campos pendientes. La guía distinguirá imagen (plantilla inmutable) de contenedor (instancia en ejecución) y capas de caché. No asumirá que las salidas locales sirven como evidencia de la VPS.

## Risks / Trade-offs

- [Alguna dependencia fijada no tiene wheel compatible con Alpine] → probar el build real primero, diagnosticar el paquete concreto y ajustar sólo lo necesario; no sumar compiladores por precaución.
- [Docker CLI presente, daemon no disponible] → dejar constancia del bloqueo ambiental y no afirmar que build, tamaño o runtime pasaron; completar esas comprobaciones al habilitar un daemon antes de cerrar el apply.
- [PostgreSQL local escucha sólo en loopback del host] → usar una base descartable alcanzable desde el contenedor y revisar su exposición; no reutilizar la DB real ni alterar la VPS para facilitar la prueba.
- [Un restart automático no cura un fallo permanente de DB/configuración] → consultar `docker ps`, logs y ready para diagnosticar; `--restart unless-stopped` se documenta para el ciclo del proceso, no como reparación de la dependencia.

## Migration Plan

No hay migración de esquema. Para probar: construir imagen, iniciar con una DB aislada, verificar salud y seed, recrear únicamente el contenedor de prueba apuntando a la misma DB y comprobar conservación. El despliegue y la reversión en la VPS se decidirán en C-08 tras revisar el destino y los comandos concretos.
