# Proposal

## Why

El proyecto cuenta con requisitos, KB y roadmap, pero todavía no tiene una aplicación ejecutable ni pruebas. Este change construye los cimientos comunes para que los siguientes changes puedan incorporar catálogo, clientes y ventas sin repetir configuración, conexiones o manejo del ciclo de vida.

## What Changes

- Crear la estructura obligatoria `app/main.py`, `app/core/{config,database}.py` y los siete módulos `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes` y `ventas`, cada uno con `models/schemas/service/router`; sólo salud incorpora comportamiento en C-01.
- Resolver dependencias compatibles con los mínimos académicos y el futuro destino Python 3.12 Alpine; configurar entorno virtual local, runner y dependencias de pruebas separadas.
- Leer `DATABASE_URL` obligatoria desde entorno o `.env`, con prioridad del entorno, sin dirección de respaldo; proponer `SQL_ECHO=false` como control de diagnóstico y entregar `env.example` ficticio.
- Administrar motor async, fábrica y cierre desde `lifespan`/`app.state`; inyectar una sesión por petición y preparar importación de modelos antes de `create_all`. Las nueve tablas se implementan en C-02.
- Exponer `GET /health/live` y `GET /health/ready`; proponer 503 con mensaje propio cuando PostgreSQL cae después de un arranque exitoso, conservando el fallo de startup si falta configuración o DB.
- Preparar PostgreSQL aislado de pruebas aprovechando los binarios locales 17 y probar configuración, startup/shutdown, sesiones y salud mediante Strict TDD.

## Capabilities

### New Capabilities

- `application-foundation`: configuración, estructura modular y ciclo de vida asincrónico de motor/sesiones, con arranque verificable y liberación de recursos.
- `health-monitoring`: contratos HTTP de liveness y readiness, incluida indisponibilidad posterior al startup.

### Modified Capabilities

Ninguna. El inventario `openspec list --specs` está vacío.

## Impact

Se incorporarán archivos de aplicación, `requirements.txt`, dependencias/configuración de pytest, `env.example`, exclusiones locales y pruebas automatizadas. Cambian dos operaciones HTTP de las 26 previstas. Los módulos de negocio quedan preparados, sin tablas, DTO de entrada ni CRUD anticipados.

La inspección de lectura detectó Python 3.14.7 por defecto, Python 3.12.14 disponible como herramienta local, PostgreSQL 17.10 y Docker CLI 29.8.2; el daemon Docker no responde y PostgreSQL no respondió en `127.0.0.1:5432`. Ningún recurso fue iniciado. El diseño concreta un clúster privado dentro del workspace y el uso local del runtime 3.12 antes de integración; no se reutilizan bases ni credenciales existentes ni se exige Codex para ejecutar la API.

Gobernanza MEDIO para sesiones y lifecycle. Configurar datos/VPS existentes conserva revisión ALTO separada. No se incluyen Dockerfile, despliegue, seed, modelos de dominio, migraciones, auth, repositorios/UoW, Compose ni publicación. Este documento propone trabajo; no declara implementación ni pruebas ejecutadas.
