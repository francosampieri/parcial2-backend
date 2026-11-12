# Descripción general

## Stack tecnológico

Las versiones de la tabla son **mínimas de la consigna**, no dependencias ya instaladas ni un archivo de versiones exactas resuelto.

| Capa | Tecnología | Versión mínima / condición |
|---|---|---|
| Lenguaje | Python | 3.12 |
| API | FastAPI | 0.111; handlers `async def` |
| Tablas y DTO | SQLModel | 0.0.24 |
| Persistencia | SQLAlchemy | 2.0, API asincrónica |
| Controlador PostgreSQL | asyncpg | 0.30 |
| Base | PostgreSQL | 16; base provista para el despliegue |
| Variables locales | python-dotenv | 1.0 |
| Servidor ASGI | uvicorn | El instalado por `fastapi[standard]` |
| Contenedor | Docker | 20.10; base obligatoria `python:3.12-alpine` |

TDD y OpenSpec provienen de las instrucciones de trabajo del usuario. El runner de pruebas automatizadas y las versiones exactas se resolverán durante los primeros changes; aún no están instalados.

## Arquitectura general

API monolítica organizada por módulo funcional:

```text
Petición HTTP → router → service → AsyncSession → PostgreSQL
                    ↘ DTO de entrada/salida
```

`router.py` recibe parámetros, inyecta la sesión y delega. `schemas.py` define contratos; `models.py`, tablas y relaciones. `service.py` contiene la lógica, las consultas con precarga y la traducción de errores.

El motor y la fábrica de sesiones nacen en `lifespan`, se guardan en `app.state` y se dispone el motor al apagar. Cada petición usa su propia sesión mediante `Depends(get_session)`. Las tablas faltantes se crean al iniciar con todos los modelos importados.

## Integraciones externas

| Servicio | Propósito | Interfaz |
|---|---|---|
| PostgreSQL | Persistencia y garantías relacionales | SQLAlchemy async + asyncpg |
| VPS | Ejecutar el contenedor y exponer una URL pública | Docker/administración del servidor, por definir acceso |
| Campus | Publicar plazo y recibir ZIP del grupo | Entrega manual; sin integración de código |

El aviso de comprobante es un log simulado con `BackgroundTasks`; no se requiere proveedor de correo. El PDF menciona VPS y base de cátedra, mientras el usuario menciona una VPS ya utilizada: verificar este punto antes de desplegar.

## API REST

| Recurso | Responsabilidad |
|---|---|
| `/health` | Liveness sin DB y readiness con `SELECT 1` |
| `/editoriales` y `/generos` | Altas, consultas y libros asociados; PATCH editorial |
| `/autores` | Alta, detalle, PATCH y libros con rol/orden |
| `/libros` | Alta con autorías, listado filtrable, detalle y PATCH |
| `/clientes` | Alta, detalle, PATCH, perfil y ventas del cliente |
| `/ventas` | Alta con renglones, listado y detalle |

El inventario completo de **26 operaciones HTTP** y sus respuestas está en [06](06_funcionalidades.md). Todos los listados respetan RN-10, incluso los que la tabla de referencia resume sin parámetros.

## Fuente

Consigna: páginas 2–3, 6–12. Detalles de implementación propuestos, no mandatos nuevos: documento 09.
