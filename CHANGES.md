# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **Librería — totones (2PRO1)**.
> Cada change agrupa una unidad técnica coherente, con el tamaño habitual de implementación y sin fragmentación artificial por motivos pedagógicos.
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**
> Estado actual: C-01 y C-02 implementados, verificados y archivados; C-03 `catalogo-y-autorias` archivado con 14/18 tareas marcadas (cuatro desviaciones TDD documentadas), aunque la funcionalidad pasó 205 pruebas; C-04 a C-08 continúan planificados. El CLI de OpenSpec conserva la fuente de verdad de los artefactos y tareas.

---

## Cómo usar este documento

1. Identificar el change y consultar `openspec list --json` y `openspec status --change "<nombre>" --json` cuando ya exista. Revisar las dependencias con el CLI: el grafo ordena el trabajo, sin imponer bloqueos de fase ni exigir archivado previo.
2. Leer los documentos de KB indicados en **Leer antes**, resolver las dudas relevantes del documento 10 y explicar propósito, alternativas y consecuencias con ejemplos comprensibles.
3. Ejecutar `/opsx:propose <nombre-del-change>` con el nombre kebab-case de este índice; después `/opsx:apply <nombre-del-change>` para implementar con TDD. Antes de modificar código existente: baseline; luego RED ejecutado, GREEN, triangulación de al menos dos casos por comportamiento y refactor con pruebas verdes. Incluir evidencia del ciclo TDD en el resumen. Los archivos `.http` y las evidencias académicas se conservan además de las pruebas automatizadas.
4. Al completar y verificar el alcance, ejecutar `/opsx:archive <nombre-del-change>` para sincronizar specs y archivar mediante la skill correspondiente. Explicar qué cambió, qué se probó y qué queda pendiente.
5. Marcar el estado `[x]` de este índice sólo cuando el alcance esté terminado y comprobado. El CLI sigue siendo la fuente de verdad de los artefactos; no crear estructura OpenSpec a mano ni presentar planificación como implementación.

La explicación didáctica acompaña propuestas, preguntas, decisiones, implementación y resúmenes. El orden es **API completa y verificada primero; Docker y publicación después**. No se agregan frontend, auth, repositorios, Unit of Work, migraciones, Redis, Compose, pagos ni reglas nuevas de inventario.

Gobernanza según las instrucciones del usuario: **BAJO** para CRUD simple/tipos/utilidades; **MEDIO** para lógica de negocio y sesiones, con checkpoints; **ALTO** para configuración que afecta datos, VPS o backup/restore, con propuesta concreta y revisión antes de ejecutar; **CRITICO** para auth, pagos, seguridad y auditoría. La venta académica registra libros y cantidades, sin pagos: no se clasifica como billing. Los cambios locales de modelos no autorizan alterar una base ya utilizada.

### Cobertura de la consigna

Los IDs `C-01` a `C-08` del roadmap identifican changes. **No son los casos C-01 a C-08 del PDF**, cuyo prefijo se aclara siempre como «caso».

| Ejercicio / requisito | Change responsable | Verificación prevista |
|---|---|---|
| Ej. 1: estructura, configuración, lifespan, sesiones y salud | C-01; registro de modelos en C-02 | Startup sobre DB vacía, cierre del motor, una sesión por petición, live sin DB, ready con SELECT 1; casos D-02/D-05 al desplegar |
| Ej. 2: nueve tablas, FK, índices, CHECK, UNIQUE y navegación | C-02 | Integración PostgreSQL de restricciones y cardinalidades; Decimal/NUMERIC y fecha con zona |
| Ej. 3: contratos, endpoints, PATCH, paginación y filtros | C-03/C-04/C-05; salud en C-01 | Las 26 operaciones de referencia; casos C-01/C-02/C-03/C-08 |
| Ej. 4: libro con autorías y venta con renglones | C-03/C-05 | Casos C-04/C-05/C-06; rollback conjunto y conservación de precios históricos |
| Ej. 5: lecturas sin N+1 | C-03/C-04/C-05; evidencia en C-06 | Precarga joinedload a uno / selectinload colecciones; caso C-07 con distinta cantidad de relaciones |
| Ej. 6: async sin bloqueos y aviso posterior | C-01/C-03/C-04/C-05 | Handlers async, concurrencia durante aviso; caso D-07 en VPS |
| Ej. 7: imagen Docker | C-07 | Build/ejecución local, Alpine, usuario, capas, exclusiones, healthcheck; evidencia final casos D-01/D-02/D-05/D-06 |
| Ej. 8: publicación y permanencia | C-08 | Casos D-01 a D-07 reales, incluyendo verificación externa D-03 y persistencia D-04 |
| Seed y test/*.http | C-06; ejecución en contenedor C-08 | Casos C-01 a C-08 con respuesta esperada en comentarios; evidencia C-07 |
| README, DEPLOY y ZIP | README en C-06; guía de contenedor C-07; cierre C-08 | Nombres de los cuatro integrantes, 2PRO1, URL y fecha/hora reales, comandos sin secretos y Parcial_Cap1a4_totones.zip |

---

## Árbol de dependencias

```text
C-01 foundation-setup
  └── C-02 core-domain-models
        │
        ├── C-03 catalogo-y-autorias ───────────┐
        │                                      │
        └── C-04 clientes-y-perfiles ──────────┤ unión obligatoria
                                               └── C-05 ventas-y-comprobantes
                                                     └── C-06 validacion-integral-y-datos
                                                           └── C-07 imagen-docker
                                                                 └── C-08 despliegue-vps-y-entrega
```

C-05 depende de **C-03 y C-04**, no de una sola rama. C-03 y C-04 comparten los modelos ya definidos en C-02; cada módulo mantiene sus propios contratos/services. Integrar las modificaciones compartidas de registro de routers de forma secuencial si se elige trabajar en paralelo.

### Paralelismo por fase

```text
GATE 0: ninguna
  → C-01 foundation-setup                    [Agente A]

GATE 1: C-01 completado
  → C-02 core-domain-models                  [Agente A]

GATE 2: C-02 completado                     ← primera bifurcación: dos ramas
  → C-03 catalogo-y-autorias                 [Agente A]
  → C-04 clientes-y-perfiles                 [Agente B]
  → Revisión de contratos/cobertura           [Agente C, sin change adicional]

GATE 3: C-03 + C-04 completados
  → C-05 ventas-y-comprobantes               [Agente A]

GATE 4: C-05 completado
  → C-06 validacion-integral-y-datos         [Agente B]

GATE 5: C-06 completado                     ← API completa y verificada
  → C-07 imagen-docker                      [Agente C]

GATE 6: C-07 completado; destino y comandos de VPS revisados
  → C-08 despliegue-vps-y-entrega            [Agente C]
```

Los gates describen disponibilidad técnica, no bloqueos del workflow OPSX. Hay siete puntos de sincronización y **una bifurcación paralela**. El plan con agentes es una distribución sugerida; este archivo no lanza agentes ni exige utilizarlos.

### Camino crítico (7 changes — mínimo irreducible)

```text
C-01 → C-02 → C-03* → C-05 → C-06 → C-07 → C-08
```

`*` La rama por **C-04** tiene la misma cantidad de nodos: `C-01 → C-02 → C-04 → C-05 → C-06 → C-07 → C-08`. Ambas ramas son obligatorias y se unen antes de ventas. Sin duraciones medidas no se puede asegurar cuál determinará el plazo: el grafo muestra siete etapas secuenciales y ocho changes totales, sin inventar horas de implementación.

### Plan óptimo con 3 agentes

| Paso | Agente A (Backend principal) | Agente B (Backend auxiliar y pruebas) | Agente C (Validación y entrega) |
|---|---|---|---|
| 1 | C-01 foundation-setup | — | — |
| 2 | C-02 core-domain-models | — | — |
| 3 | C-03 catalogo-y-autorias | C-04 clientes-y-perfiles | Revisar cobertura de contratos sin editar los mismos archivos |
| 4 | C-05 ventas-y-comprobantes | — | — |
| 5 | — | C-06 validacion-integral-y-datos | — |
| 6 | — | — | C-07 imagen-docker |
| 7 | — | — | C-08 despliegue-vps-y-entrega, tras revisión de operaciones concretas |

No hay frontend al que asignar un agente. La dependencia de datos y el pedido de terminar la API antes de empaquetarla limitan el paralelismo; no se inventan tareas para ocupar tres agentes.

---

## FASE 1 — Cimientos y modelo relacional

### [C-01] `foundation-setup`
- **Estado**: `[x]` implementado, verificado y [archivado](openspec/changes/archive/2026-11-11-foundation-setup/) (11/11/2026); specs sincronizadas. Evidencia: [TDD-C01](docs/evidencia/TDD-C01.md).
- **Scope**:
  - Crear `app/main.py`, `app/core/config.py`, `app/core/database.py` y estructura modular obligatoria; resolver versiones compatibles con los mínimos de la consigna y registrar dependencias en `requirements.txt`.
  - Leer DATABASE_URL requerida desde entorno/.env sin fallback, entregar `env.example` sin secretos y diagnóstico SQL configurable; no escribir credenciales reales. Preparar el runner y una DB de pruebas aislada antes de pruebas de integración.
  - Crear motor async y fábrica de sesiones en lifespan, conservarlos en app.state, usar Depends(get_session), una AsyncSession por petición, expire_on_commit=False, create_all y dispose al apagar. Preparar punto único de importación de los modelos que C-02 completará.
  - Implementar GET /health/live con {"estado":"vivo"} sin DB y GET /health/ready con SELECT 1. Concretar la propuesta de 503 propio si DB cae después de iniciar; startup debe fallar sin URL o sin DB disponible.
  - Pruebas TDD: contratos de salud, falta de configuración, DB inaccesible, cierre de recursos y aislamiento de sesiones. No declarar probado el arranque de las nueve tablas hasta C-02.
  - Explicar FastAPI, ASGI/uvicorn, async/await, lifespan, inyección de dependencias y diferencia entre estar vivo y estar listo para atender.
- **Dependencias**: ninguna
- **Governance**: MEDIO — ciclo de vida y sesiones; archivos de ejemplo locales sin cambios sobre datos reales. Configuración de una base/VPS existente requiere revisión aparte.
- **Leer antes**:
  - [02 — Descripción general](knowledge-base/02_descripcion_general.md) §Stack tecnológico y Arquitectura general
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §Épica 1: Aplicación y salud
  - [07 — Flujos principales](knowledge-base/07_flujos_principales.md) §Flujo 1: Arranque y apagado
  - [08 — Arquitectura propuesta](knowledge-base/08_arquitectura_propuesta.md) §Ciclo de vida y persistencia
  - [10 — Preguntas abiertas](knowledge-base/10_preguntas_abiertas.md) §Preguntas abiertas priorizadas, PA-03/PA-07

### [C-02] `core-domain-models`
- **Estado**: `[x]` implementado, verificado y [archivado](openspec/changes/archive/2026-11-12-core-domain-models/) (12/11/2026); specs sincronizadas. Evidencia: [TDD-C02](docs/evidencia/TDD-C02.md), con desviaciones de Strict TDD documentadas.
- **Scope**:
  - Declarar las nueve tablas con nombres y columnas exactos: Editorial, Genero, Autor, Libro, LibroAutor, Cliente, PerfilCliente, Venta y RenglonVenta, dentro de sus módulos obligatorios.
  - Implementar UNIQUE de nombre editorial/género, ISBN, email y cliente_id del perfil; PK compuesta de LibroAutor, todos los CHECK, FK e índices. Representar dinero con Decimal/NUMERIC y fecha con zona horaria.
  - Declarar navegación bidireccional con back_populates; Cliente.perfil es objeto opcional. Mantener rol/orden en LibroAutor y propiedad de renglones en venta, sin link_model que oculte datos ni repositorios/UoW.
  - Completar imports antes de create_all y verificar arranque sobre DB vacía sin migraciones. Pruebas de restricciones, asociaciones, perfil único, rollback y conservación de tablas/datos ya existentes; trabajar sobre DB aislada, sin recrear esquema de otro proyecto.
  - Explicar tablas versus objetos, PK/FK, UNIQUE/CHECK/índices, agregación/asociación/composición, uno a uno y muchos a muchos con atributos; mostrar por qué cada FK está de ese lado.
- **Dependencias**: C-01
- **Governance**: MEDIO — integridad y relaciones del dominio; no constituye autorización para modificar un esquema ya utilizado en VPS.
- **Leer antes**:
  - [04 — Modelo de datos](knowledge-base/04_modelo_de_datos.md) §ERD y Entidades
  - [05 — Reglas de negocio](knowledge-base/05_reglas_de_negocio.md) §Catálogo, Clientes y Ventas
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §Épicas 2 a 4
  - [08 — Arquitectura propuesta](knowledge-base/08_arquitectura_propuesta.md) §Ciclo de vida y persistencia
  - [09 — Decisiones y supuestos](knowledge-base/09_decisiones_y_supuestos.md) §DD-02 y DD-03

---

## FASE 2 — API de catálogo, clientes y ventas

> C-03 y C-04 pueden implementarse en paralelo una vez definido C-02. C-05 integra ambas capacidades. Las pruebas relevantes se escriben dentro de cada change, no se postergan a C-06.

### [C-03] `catalogo-y-autorias`
- **Estado**: `[~]` archivado con advertencia — 14/18 tareas marcadas; [archivo OpenSpec](openspec/changes/archive/2026-11-12-catalogo-y-autorias/) y [evidencia TDD](docs/evidencia/TDD-C03.md). Cuatro tareas permanecen abiertas por RED específico omitido; 205 pruebas funcionales pasaron.
- **Scope**:
  - Crear schemas Create/Update/Read y services/routers de editoriales, géneros, autores y libros, separados de los modelos de tabla; registrar sus routers.
  - Implementar las 16 operaciones: POST/GET /editoriales/, GET/PATCH /editoriales/{id}, GET /editoriales/{id}/libros; POST/GET /generos/, GET /generos/{id}/libros; POST /autores/, GET/PATCH /autores/{id}, GET /autores/{id}/libros; POST/GET /libros/, GET/PATCH /libros/{id}.
  - Alta de libro por editorial_id, genero_id opcional y autores con autor_id/rol/orden. Escribir sin SELECT previo de unicidad ni existencia de FK; concretar transacción conjunta y traducir IntegrityError con rollback a 409 propio.
  - Implementar PATCH con exclude_unset y decidir explícitamente la semántica de autorías y NULL. Concretar mínimo de una autoría según figura 1 como interpretación registrada, no como una nueva regla textual del PDF.
  - Paginar todos los listados con limit=20, rango 1–100, offset>=0; filtrar libros por título parcial sin mayúsculas mediante parámetros ligados y por genero_id. Concretar orden estable; devolver rol/orden en libros del autor, editorial/género en listado y autores en detalle de libro.
  - Precargar relaciones con joinedload a uno y selectinload colecciones; cubrir casos del PDF C-01, C-02 (ISBN), C-04 y C-08, validaciones/PATCH y número fijo de consultas al variar autores. No devolver SQL ni trazas.
  - Explicar router/service/DTO, validación 422, códigos 201/404/409, PATCH parcial, parámetros ligados, objeto de asociación y cómo reconocer N+1.
- **Dependencias**: C-02
- **Governance**: MEDIO — CRUD y consultas con alta relacional transaccional; sin reglas de disponibilidad de stock.
- **Leer antes**:
  - [04 — Modelo de datos](knowledge-base/04_modelo_de_datos.md) §Entidades y Navegación bidireccional
  - [05 — Reglas de negocio](knowledge-base/05_reglas_de_negocio.md) §Catálogo y Excepciones globales y contratos
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §Épica 2: Catálogo
  - [07 — Flujos principales](knowledge-base/07_flujos_principales.md) §Flujos 2 y 3
  - [10 — Preguntas abiertas](knowledge-base/10_preguntas_abiertas.md) §PA-04/PA-05/PA-10/PA-11

### [C-04] `clientes-y-perfiles`
- **Estado**: `[x]` implementado, verificado y [archivado](openspec/changes/archive/2026-11-12-clientes-y-perfiles/) (12/11/2026); 14/14 tareas y specs sincronizadas. Evidencia: [TDD-C04](docs/evidencia/TDD-C04.md); 227 pruebas pasaron.
- **Scope**:
  - Crear schemas, services y routers de clientes/perfiles con contratos separados; implementar POST /clientes/, GET/PATCH /clientes/{id} y POST /clientes/{id}/perfil. La consulta de ventas del cliente pertenece a C-05 para no crear una dependencia circular.
  - Proteger email y perfil único con la DB, sin preconsulta de unicidad. Cliente inexistente en detalle/PATCH/alta de perfil devuelve 404; email repetido o segundo perfil, 409 con mensaje propio y rollback.
  - Leer perfil con precarga y devolver objeto opcional; PATCH aplica sólo campos enviados y define NULL conforme al contrato. Mantener handlers async y sesión inyectada.
  - Pruebas TDD: casos del PDF C-02 (email), C-03, IDs no enteros/inexistentes, cliente con/sin perfil, PATCH parcial y respuesta sin detalles internos. No agregar login ni roles.
  - Explicar uno a uno mediante FK única, diferencia entre entidad cliente y usuario autenticado, DTO de salida y tratamiento de omisión frente a NULL.
- **Dependencias**: C-02
- **Governance**: BAJO — CRUD simple y perfil único, con autonomía si las pruebas pasan; no modificar configuración real de datos.
- **Leer antes**:
  - [03 — Actores y roles](knowledge-base/03_actores_y_roles.md) §Actores del sistema y Rutas públicas
  - [04 — Modelo de datos](knowledge-base/04_modelo_de_datos.md) §Entidades y Navegación bidireccional
  - [05 — Reglas de negocio](knowledge-base/05_reglas_de_negocio.md) §Clientes y Excepciones globales y contratos
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §Épica 3: Clientes
  - [07 — Flujos principales](knowledge-base/07_flujos_principales.md) §Flujos 3 y 4

### [C-05] `ventas-y-comprobantes`
- **Estado**: `[ ]` pendiente
- **Scope**:
  - Crear schemas/services/router de ventas e implementar POST/GET /ventas/, GET /ventas/{id} y GET /clientes/{id}/ventas. Los listados son paginados y la consulta por cliente inexistente responde 404.
  - Aceptar cliente_id y renglones con libro_id/cantidad, mínimo uno y sin repetir libro; no aceptar precio, total ni fecha como datos de la venta. Libro/cliente inexistente al crear devuelve 409 propio; DTO inválido, 422.
  - Leer precios de libros de forma agrupada, copiarlos con Decimal y calcular subtotales/total y fecha con zona. Confirmar cabecera/renglones juntos, sin persistencia parcial; conservar el precio histórico ante PATCH posterior del libro.
  - Devolver cliente y renglones con título, cantidad, precio y subtotal mediante precarga; número fijo de consultas al variar renglones. No implementar PATCH de venta, alta suelta de renglones ni descuento/control de stock.
  - Agendar tras alta confirmada un BackgroundTasks async con await asyncio.sleep(0.5) y log de comprobante después de responder; no reutilizar la sesión cerrada ni bloquear otras peticiones.
  - Pruebas TDD: casos del PDF C-05/C-06 y parte de C-07, lista vacía/duplicados/cantidad inválida, precios históricos, rollback, aviso posterior y concurrencia sin bloqueos. Completar así las 26 operaciones de referencia.
  - Explicar composición y DTO anidado, transacciones/commit/rollback, Decimal, copia histórica y diferencia entre tarea posterior a respuesta y una cola externa.
- **Dependencias**: C-03, C-04
- **Governance**: MEDIO — lógica de ventas académicas y transacciones, sin pagos ni billing. Presentar decisiones no obvias con ejemplos.
- **Leer antes**:
  - [04 — Modelo de datos](knowledge-base/04_modelo_de_datos.md) §Datos calculados y DTO
  - [05 — Reglas de negocio](knowledge-base/05_reglas_de_negocio.md) §Ventas
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §Épica 4: Ventas
  - [07 — Flujos principales](knowledge-base/07_flujos_principales.md) §Flujo 5: Registrar venta y avisar
  - [09 — Decisiones y supuestos](knowledge-base/09_decisiones_y_supuestos.md) §PR-01 y SU-03

---

## FASE 3 — API verificada y demostración reproducible

### [C-06] `validacion-integral-y-datos`
- **Estado**: `[ ]` pendiente
- **Scope**:
  - Crear comando de datos iniciales explícito que deje datos conocidos para las demostraciones y permita repetición segura. Resolver IDs/datos del ejemplo; separar cualquier reset en DB aislada, sin borrar datos del servidor ni de otro proyecto.
  - Entregar archivos test/*.http con los casos del PDF C-01 a C-08, comentarios de respuesta esperada y secuencia reproducible. Mantener las pruebas TDD ya implementadas; cubrir sólo huecos conductuales reales del recorrido integral.
  - Ejecutar el recorrido completo de las 26 operaciones, PATCH parcial, paginación/filtros, errores propios y venta con dos renglones. Validar arranque sobre DB vacía y que reiniciar no elimine datos.
  - Capturar evidencia real C-07 del detalle de libro y venta, comparando uno y varios autores/renglones; verificar cantidad fija de consultas con SQL configurable y guardar fragmentos sanitizados en evidencia/.
  - Escribir README desde cero: entorno virtual, requirements, env.example/.env sin secretos, inicio que crea tablas y comando seed; identificar totones, Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria, curso 2PRO1.
  - Explicar seed frente a create_all, pruebas unitarias/integración/HTTP, ciclo RED/GREEN/triangulación y cómo leer el SQL para comprobar N+1. Resumir qué exige el PDF y qué agrega TDD como proceso de trabajo.
- **Dependencias**: C-05
- **Governance**: MEDIO — datos iniciales y recorrido integral en entorno aislado. Operaciones de reset sobre datos reales serían ALTO y no están autorizadas por este scope.
- **Leer antes**:
  - [01 — Visión y objetivos](knowledge-base/01_vision_y_objetivos.md) §Métricas de éxito
  - [04 — Modelo de datos](knowledge-base/04_modelo_de_datos.md) §Seed data inicial
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §Épica 5: Verificación y entrega
  - [08 — Arquitectura propuesta](knowledge-base/08_arquitectura_propuesta.md) §Verificación y evidencias y Documentación y paquete de entrega
  - [10 — Preguntas abiertas](knowledge-base/10_preguntas_abiertas.md) §PA-06

---

## FASE 4 — Contenedor, publicación y entrega

### [C-07] `imagen-docker`
- **Estado**: `[ ]` pendiente
- **Scope**:
  - Crear Dockerfile desde python:3.12-alpine; copiar/instalar requirements.txt con --no-cache-dir antes del código, verificar dependencias en Alpine sin agregar compiladores innecesarios y ejecutar con usuario no root.
  - Crear .dockerignore que excluya .env, .venv, .git y __pycache__; no incorporar secretos en capas ni configuración real de DB en la imagen.
  - Ejecutar uvicorn app.main:app en 0.0.0.0:8000 y declarar HEALTHCHECK con http://127.0.0.1:8000/health/ready. Preparar docker run con puerto parametrizado, --env-file y --restart unless-stopped; PostgreSQL permanece externo, sin Compose.
  - Construir y comprobar el contenedor en entorno de pruebas: startup con create_all, estado healthy, seed por docker exec, proceso no root, fallo sin URL/DB y persistencia al recrearlo. Medir tamaño de la base (<100 MB), distinguiéndolo del tamaño final; no presentar resultados locales como evidencia D del VPS.
  - Preparar DEPLOY.md con procedimiento y comandos parametrizados para revisión; marcar URL, fecha/hora y evidencias de VPS como pendientes. Documentar cualquier corrección necesaria para correr en contenedor.
  - Explicar imagen versus contenedor, capas y caché, puertos interno/externo, env-file, usuario, healthcheck/restart y por qué localhost dentro del contenedor no apunta a PostgreSQL del host.
- **Dependencias**: C-06
- **Governance**: BAJO — empaquetado y comprobación local sin cambios sobre VPS ni variables reales; configuración que afecte datos se revisa antes de ejecutarse.
- **Leer antes**:
  - [01 — Visión y objetivos](knowledge-base/01_vision_y_objetivos.md) §Alcance v1.0 y Métricas de éxito
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §US-008 — Publicar y entregar
  - [07 — Flujos principales](knowledge-base/07_flujos_principales.md) §Flujo 7: Publicación y actualización
  - [08 — Arquitectura propuesta](knowledge-base/08_arquitectura_propuesta.md) §Docker y red
  - [09 — Decisiones y supuestos](knowledge-base/09_decisiones_y_supuestos.md) §DD-05

### [C-08] `despliegue-vps-y-entrega`
- **Estado**: `[ ]` pendiente
- **Scope**:
  - Inspeccionar y confirmar VPS autorizada, PostgreSQL/base/usuario, puerto/URL y proyecto ya alojado. Resolver PA-01/PA-02 y fecha límite del campus; preparar para revisión los comandos exactos y cambios de configuración necesarios, sin publicar credenciales ni interrumpir el otro proyecto.
  - Tras revisión explícita de las operaciones ALTO, construir o transferir la imagen y correrla con docker run, puerto asignado, variables fuera del repo/imagen, SQL_ECHO=false y restart unless-stopped. Si DB está en host Linux, revisar dirección/puertos y --add-host=host.docker.internal:host-gateway sin asumir configuración del servidor.
  - Ejecutar seed con docker exec; comprobar desde fuera GET /health/ready (200), GET /libros/ con datos (200) y POST /ventas/ del ejemplo (201 con precios copiados/total). Mantener servicio accesible hasta la publicación de notas.
  - Ejecutar y guardar comandos/salidas reales de los casos D-01 a D-07 en evidencia/: imágenes/base Alpine, build/run healthy y logs, prueba externa, recreación conservando datos, fallo sin DATABASE_URL, id no root y aviso posterior. Recrear únicamente el contenedor de este parcial; no ejecutar borrados globales ni tocar DB del proyecto existente.
  - Completar DEPLOY.md con URL pública, fecha/hora reales, build/run completos sin secretos, nombre del env-file, ajustes y actualización por reconstrucción/recreación. Revisar README con los cuatro integrantes y reunir evidencia C-07 y D; no inventar resultados ni marcar completado si falta un caso requerido.
  - Preparar Parcial_Cap1a4_totones.zip con una carpeta de fuente, requirements.txt, env.example, test/, Dockerfile/.dockerignore, README, DEPLOY y evidencia; excluir .env/.venv/__pycache__ y evitar .git. La subida al campus la realiza un integrante; este roadmap no autoriza enviarla automáticamente.
  - Guiar el despliegue explicando red contenedor/host/DB, diagnóstico por logs, healthy, persistencia externa y actualización; presentar lo observado y lo pendiente con lenguaje accesible.
- **Dependencias**: C-07
- **Governance**: ALTO — publicación/configuración de VPS y datos reales: proponer cambios concretos y esperar revisión antes de escribir/ejecutar lo que afecte ese entorno. La planificación y la inspección de lectura pueden avanzar previamente.
- **Leer antes**:
  - [01 — Visión y objetivos](knowledge-base/01_vision_y_objetivos.md) §Métricas de éxito
  - [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) §US-008 — Publicar y entregar
  - [07 — Flujos principales](knowledge-base/07_flujos_principales.md) §Flujo 7: Publicación y actualización
  - [08 — Arquitectura propuesta](knowledge-base/08_arquitectura_propuesta.md) §Docker y red, Verificación y evidencias y Documentación y paquete de entrega
  - [10 — Preguntas abiertas](knowledge-base/10_preguntas_abiertas.md) §PA-01/PA-02/PA-09


