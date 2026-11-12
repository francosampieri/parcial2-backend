# Arquitectura propuesta

## Patrones aplicados

| Patrón / mecanismo | Dónde | Motivo |
|---|---|---|
| Módulos funcionales | app/modules | Estructura obligatoria del PDF |
| Router → service | Cada módulo | Separar HTTP de lógica sin repositorios/UoW |
| DTO separados de tablas | schemas / models | Contratos de entrada/salida controlados |
| Inyección de dependencias | Depends(get_session) | Una sesión por petición |
| Lifespan | app/main.py y core/database.py | Crear/disponer recursos y crear tablas |
| Objeto de asociación | LibroAutor | Rol y orden pertenecen a la relación |
| Carga anticipada | Consultas de service | Evitar lazy loading y N+1 |
| BackgroundTasks async | Alta de venta | Simular aviso sin bloquear respuesta |

## Estructura de directorios

Estructura objetivo, todavía no implementada:

    app/
      main.py
      core/
        config.py
        database.py
      modules/
        health/        # models.py, schemas.py, service.py, router.py
        editoriales/   # misma estructura
        generos/
        autores/
        libros/        # incluye LibroAutor
        clientes/      # incluye PerfilCliente
        ventas/        # incluye RenglonVenta
    test/
      *.http
    requirements.txt
    env.example
    Dockerfile
    .dockerignore
    README.md
    DEPLOY.md
    evidencia/

La tabla de estructura del PDF aplica el mismo formato a los módulos, incluido health; no crear entidades ficticias para salud. Los archivos sin modelos de tabla pueden explicitar ese hecho. La ubicación de pruebas automatizadas adicionales se resolverá con el runner, conservando test/*.http.

## Ciclo de vida y persistencia

- Leer DATABASE_URL desde entorno/.env, sin valor por defecto. No crear conexiones al importar un módulo.
- Crear motor async y fábrica de sesiones dentro de lifespan; guardarlos en app.state.
- Importar los nueve modelos antes de ejecutar SQLModel.metadata.create_all a través de conexión async.
- Una AsyncSession por petición con expire_on_commit=False; cerrar sesión al finalizar y disponer motor al apagar.
- Las operaciones compuestas de alta libro/autorías y venta/renglones deben confirmarse juntas. Rollback ante error antes de reutilizar sesión.
- Guardar dinero como Decimal/NUMERIC y fecha de venta con zona horaria.
- No usar migraciones para cumplir este parcial. create_all no actualiza tablas existentes: documentar esta limitación y usar DB de pruebas aislada para iterar modelos.

## Consultas, DTO y errores

DTO Create sin id; Update parcial; Read con relaciones expresamente necesarias. Separar representación del listado y del detalle cuando ayude a evitar ciclos y datos de más.

Precargar relaciones a uno con joinedload y colecciones con selectinload. Ejemplos de estrategia: libro con editorial/género y autorías→autor; venta con cliente y renglones→libro. Las consultas relacionadas deben mantener cantidad fija al aumentar sus elementos.

Traducir IntegrityError en el service con mensaje de dominio y 409, sin filtrar SQL, nombres de restricciones o tablas. DB impone UNIQUE/FK/CHECK. No verificar unicidad con consulta previa. Alta de libro tampoco consulta antes si cada FK existe. Las lecturas necesarias para precios de venta siguen siendo parte del caso de uso.

## Seguridad y configuración

- Autenticación/autorización fuera de alcance; rutas públicas.
- Validación por DTO y Query; consultas parametrizadas, nunca SQL concatenado con entrada del usuario.
- Secretos sólo en entorno/archivo local excluido de control de versiones y contexto Docker.
- env.example usa marcadores ficticios y se llama así, sin punto inicial.
- Los logs/evidencias no deben incluir credenciales ni capturas de variables reales.

| Variable | Descripción | Ejemplo sin secreto | Sensible |
|---|---|---|---|
| DATABASE_URL | URL requerida de PostgreSQL async | postgresql+asyncpg://USUARIO:CLAVE@HOST:5432/BASE | Sí en configuración real |
| SQL_ECHO | Propuesta para diagnóstico SQL configurable | false; activar sólo para evidencia local | No |

No establecer URL real ni fallback. El nombre SQL_ECHO es una propuesta concreta para el requisito de diagnóstico configurable, no un nombre fijado por el PDF.

## Docker y red

- FROM python:3.12-alpine obligatorio. El límite menor a 100 MB corresponde a esa **base**, no a la imagen final; medir en la evidencia real.
- Copiar/instalar requirements.txt antes del código y con --no-cache-dir.
- Crear usuario sin privilegios y activar USER. Excluir .env, .venv, .git y __pycache__ con .dockerignore.
- Ejecutar uvicorn app.main:app en 0.0.0.0:8000.
- HEALTHCHECK a http://127.0.0.1:8000/health/ready; evitar localhost por resolución IPv6 de herramientas Alpine.
- DB fuera del contenedor de aplicación. Sin Compose ni base empaquetada.
- Forma del comando de referencia, con marcadores que deben reemplazarse antes de usar:

    docker run -d --name libreria -p <PUERTO_ASIGNADO>:8000 --restart unless-stopped --env-file <ARCHIVO_DE_VARIABLES> libreria

Si PostgreSQL está en host Linux, revisar --add-host=host.docker.internal:host-gateway, dirección de escucha y acceso permitido. No asumir que localhost dentro del contenedor alcanza al host ni modificar red/firewall sin revisar la VPS existente.

La instalación de dependencias debe verificarse en Alpine con las versiones elegidas. El PDF indica que el stack se instala sin compiladores; no incorporar paquetes del sistema por costumbre.

## Verificación y evidencias

Strict TDD se aplica a implementación con runner disponible por instrucciones del usuario: baseline, RED ejecutado, GREEN, triangulación y refactor. No sustituye los .http del parcial ni exige pruebas artificiales de archivos documentales.

| Caso | Evidencia / resultado |
|---|---|
| C-01 | Ruta con ID no entero: 422 sin ejecutar handler |
| C-02 | ISBN o email duplicado: 409 propio |
| C-03 | Segundo perfil: 409 |
| C-04 | Libro con editorial o autor inexistente: 409 propio |
| C-05 | Venta con libro o cliente inexistente: 409 |
| C-06 | Venta de dos renglones: 201, precios copiados y total correcto |
| C-07 | Logs SQL de detalle libro/venta: cantidad fija con uno y varios elementos; guardar en evidencia/ |
| C-08 | Título ' OR '1'='1: 200 y lista vacía sobre datos conocidos |
| D-01 | docker images base y proyecto; base Alpine <100 MB |
| D-02 | Build/run, docker ps healthy y logs con arranque/tablas |
| D-03 | Desde fuera del VPS: ready 200, libros con seed 200, venta 201 |
| D-04 | Recrear sólo contenedor del parcial; healthy y datos conservados |
| D-05 | Sin DATABASE_URL: termina con error, no queda sirviendo |
| D-06 | docker exec libreria id: proceso no root |
| D-07 | Aviso de comprobante en logs después de respuesta |

Los casos D se ejecutan sobre el despliegue VPS y conservan comandos y salidas en evidencia/. No fabricar resultados cuando Docker/VPS no esté disponible.

## Documentación y paquete de entrega

- README: nombres/apellidos y pasos locales desde cero, entorno virtual, dependencias, .env, arranque y seed.
- DEPLOY: URL pública, día/hora reales, build/run completos sin secretos, nombre del archivo de variables, ajustes realizados y procedimiento de actualización.
- ZIP: una carpeta con fuente, requirements.txt, env.example, test/, Dockerfile, .dockerignore, README, DEPLOY y evidencia.
- Excluir .env, .venv y __pycache__. Conviene excluir .git; si se entrega, el historial también se revisa.
- Formato Parcial_Cap1a4_<NombreDelGrupo>.zip; nombre confirmado: Parcial_Cap1a4_totones.zip. Plazo en campus.

## Fuente

Consigna: páginas 3, 6–16. Runner, nombre SQL_ECHO y detalles de organización de tests son propuestas pendientes.
