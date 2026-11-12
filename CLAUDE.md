# Librería — totones (2PRO1): Instrucciones para Agentes

> Fuente de instrucciones del proyecto para Codex y otros agentes. Mantener AGENTS.md y CLAUDE.md con el mismo contenido.
> Grupo: Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria. Entrega: Parcial_Cap1a4_totones.zip.
> Generado desde la KB, CHANGES.md, el registro de skills y las reglas confirmadas por el usuario.

## Stack Tecnológico

Las versiones siguientes son mínimos de la consigna, no un lock de dependencias ya resuelto.

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

Detalle: [descripción general](knowledge-base/02_descripcion_general.md). La API es un monolito modular asincrónico de catálogo, clientes y ventas. No se solicita frontend, auth, pagos, repositorios, Unit of Work, migraciones, Redis ni Compose.

## Base de Conocimiento

Leer la fuente pertinente antes de proponer o implementar. Conservar trazabilidad con RN-01 a RN-12, casos C-01 a C-08 y D-01 a D-07 de la consigna.

| Archivo | Cuándo leerlo |
|---|---|
| [Índice de KB](knowledge-base/README.md) | Fuentes y recorrido de lectura |
| [01 — Visión y objetivos](knowledge-base/01_vision_y_objetivos.md) | Alcance, evaluación y entrega |
| [02 — Descripción general](knowledge-base/02_descripcion_general.md) | Stack y arquitectura general |
| [03 — Actores y roles](knowledge-base/03_actores_y_roles.md) | Responsabilidades y acceso público; sin RBAC |
| [04 — Modelo de datos](knowledge-base/04_modelo_de_datos.md) | Nueve tablas, relaciones, restricciones y seed |
| [05 — Reglas de negocio](knowledge-base/05_reglas_de_negocio.md) | Reglas de catálogo, clientes y ventas |
| [06 — Funcionalidades](knowledge-base/06_funcionalidades.md) | Las 26 operaciones HTTP y criterios de aceptación |
| [07 — Flujos principales](knowledge-base/07_flujos_principales.md) | Arranque, altas, lecturas, ventas y publicación |
| [08 — Arquitectura propuesta](knowledge-base/08_arquitectura_propuesta.md) | Módulos, sesiones, configuración, Docker y pruebas |
| [09 — Decisiones y supuestos](knowledge-base/09_decisiones_y_supuestos.md) | Distinguir mandatos, decisiones confirmadas y propuestas |
| [10 — Preguntas abiertas](knowledge-base/10_preguntas_abiertas.md) | Resolver cada duda antes del change al que afecta |

Fuentes originales: [consigna académica](docs/consigna-parcial.pdf) y [contexto del grupo](docs/contexto-del-grupo.md). Distinguir requisitos del PDF de instrucciones del usuario y de ejemplos de bibliotecas.

Antes de C-01, comprobar el entorno y preparar PostgreSQL aislado para integración (PA-03). Confirmar VPS/base/puerto/servicios existentes antes de C-08 (PA-01/PA-02); esas dudas no bloquean el desarrollo local. PATCH de autorías/NULL, seed y readiness 503 se resuelven en los changes pertinentes, sin presentarlos como decisiones ya confirmadas.

## Skills Disponibles

Usar [.atl/skill-registry.md](.atl/skill-registry.md) como catálogo de nombres, triggers y rutas; no volver a escanear por cada tarea. Las versiones del proyecto prevalecen sobre duplicados globales.

| Agente / rol | Responsabilidad | Skills pertinentes |
|---|---|---|
| Backend core y auxiliar | Modelos, servicios y rutas | `openspec-apply-change`; `supabase-postgres-best-practices` para persistencia; `python-testing-patterns` para pruebas |
| Pruebas y validación | Contratos, integración, regresión y N+1 | `python-testing-patterns`, `supabase-postgres-best-practices`; `review-agent` cuando se delegue revisión y esté disponible |
| Orquestación OPSX | Consultar estado, proponer, explorar, actualizar, aplicar y archivar | Las seis `openspec-*` registradas: explore, propose, update-change, apply-change, sync-specs y archive-change |
| Fundación y documentación | Mantener KB, roadmap e instrucciones | `active-orchestrator`, `kb-creator`, `roadmap-generator`, `find-skills`, `skill-registry`, `agents-md-generator`; las herramientas de registro/generación se consultan por su instalación conocida |
| Entrega / Docker / VPS | Empaquetado y publicación conforme al parcial | `openspec-apply-change`; documentación oficial; `review-agent` si corresponde. No se instaló una skill Docker |
| Lectura de consigna | Consultar el PDF original | `pdf` cuando haga falta revisar sus páginas |

Las guías de dominio locales están en [.agents/skills/python-testing-patterns/SKILL.md](.agents/skills/python-testing-patterns/SKILL.md) y [.agents/skills/supabase-postgres-best-practices/SKILL.md](.agents/skills/supabase-postgres-best-practices/SKILL.md). Las seis OpenSpec también están instaladas en el proyecto. Otras guías del catálogo dependen de su disponibilidad en el equipo; no inventar que están instaladas al clonar.

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo).

La referencia anterior describe su uso como artefacto local: el archivo existe en este workspace. No se detectó .gitignore al generar estas instrucciones; asegurar la exclusión de .atl/ cuando se prepare el control de versiones. Si falta el registro en otro equipo, regenerarlo con la skill disponible; no asumir que sus rutas absolutas de otro equipo son válidas. No copiar aquí los bloques compactos.

## Roadmap de Changes

[CHANGES.md](CHANGES.md) contiene scope, dependencias, gobernanza y lecturas previas. Son **8 changes en 4 fases**, todavía planificados al generar estas instrucciones.

| ID | Nombre | Dependencias |
|---|---|---|
| C-01 | `foundation-setup` | Ninguna |
| C-02 | `core-domain-models` | C-01 |
| C-03 | `catalogo-y-autorias` | C-02 |
| C-04 | `clientes-y-perfiles` | C-02 |
| C-05 | `ventas-y-comprobantes` | C-03 y C-04 |
| C-06 | `validacion-integral-y-datos` | C-05 |
| C-07 | `imagen-docker` | C-06 |
| C-08 | `despliegue-vps-y-entrega` | C-07 |

C-03 y C-04 admiten paralelismo; ambas ramas son necesarias antes de ventas. El grafo tiene siete etapas secuenciales; sin duraciones medidas no se promete un plazo mínimo. Los gates son dependencias técnicas, no bloqueos rígidos del workflow OPSX.

Primer change: `foundation-setup`. Próxima propuesta, una vez cerrado el checkpoint de fundación: `/opsx:propose foundation-setup`. Los IDs de changes C-NN y los casos C-NN del PDF son numeraciones distintas.

## Reglas Duras (específicas del proyecto)

No existe un CLAUDE.md global en la ubicación inspeccionada. Estas instrucciones cubren el contrato del proyecto y las reglas universales ya indicadas por el usuario; no afirman herencia de un archivo ausente.

### Contrato de implementación confirmado

1. **Nombres y tipos:** usar snake_case en funciones/variables y anotaciones de tipos en las funciones y contratos Python. Mantener los nombres obligatorios de tablas/columnas.
2. **Entradas explícitas:** configurar `extra='forbid'` en los DTO de entrada, incluidos Create, Update y entradas anidadas. Rechazar campos no declarados con validación 422; los campos obligatorios/opcionales se definen por separado. Esta política adicional fue aprobada por el usuario, no impuesta textualmente por el PDF.
3. **Altas compuestas atómicas:** libro con todas sus autorías y venta con todos sus renglones se confirman como una operación conjunta. Si falla una parte, rollback de toda el alta; no persistir datos parciales.
4. **Módulos y contratos:** conservar app/main.py, core/config.py, core/database.py y los siete módulos con models/schemas/service/router. La lógica vive en service con sesión explícita. DTO separados de tablas; altas sin id y PATCH sólo con campos enviados mediante exclude_unset.
5. **Asincronía:** todos los handlers async def, sin time.sleep, requests ni DB síncrona. Aviso de comprobante con BackgroundTasks async y await asyncio.sleep(0.5), después de responder.
6. **Ciclo de vida:** crear motor/fábrica en lifespan/app.state y disponer el motor al apagar. Una sesión por petición con Depends y expire_on_commit=False. Importar modelos antes de create_all; éste no altera tablas existentes ni autoriza resets.
7. **Configuración:** DATABASE_URL requerida desde entorno/.env sin dirección de respaldo; startup falla si falta o la DB no está disponible. env.example sin valores reales. Diagnóstico SQL configurable.
8. **Integridad:** UNIQUE, CHECK, FK, índices y back_populates según el modelo. Cliente.perfil es objeto opcional; LibroAutor conserva rol/orden. No consultar previamente unicidad; alta de libro tampoco preconsulta existencia de FK. Traducir IntegrityError y hacer rollback, sin devolver SQL ni trazas.
9. **Ventas:** dinero Decimal/NUMERIC, fecha con zona; copiar precios desde los libros, calcular total/subtotales y conservar precios históricos. Sin PATCH de ventas, alta suelta de renglones ni reglas nuevas de descuento/disponibilidad de stock.
10. **Lecturas:** precargar toda relación usada: joinedload a uno y selectinload colecciones, sin lazy loading. Consultas parametrizadas y número fijo de consultas al variar autores/renglones. Todo listado usa limit=20, entre 1–100, y offset>=0.
11. **Pruebas:** conservar Strict TDD y verificar integración con PostgreSQL aislado; no sustituir aceptación relacional con SQLite ni limpiar datos reales. Mantener .http C-01 a C-08 y evidencia real C-07/D-01 a D-07. No inventar resultados.
12. **Contenedor:** python:3.12-alpine, instalar requirements antes del código, usuario no root, uvicorn 0.0.0.0:8000 y HEALTHCHECK ready en 127.0.0.1. DB externa, docker run sin Compose; límite <100 MB para imagen base, no final.
13. **Secretos y entrega:** nunca credenciales reales en fuente, repositorio, imagen, evidencias o ZIP. Excluir .env/.venv/.git/__pycache__ del contexto Docker según consigna. Documentar URL y fecha/hora reales de publicación, sin anticiparlas; mantener la API en línea hasta notas.
14. **Didáctica y autonomía:** explicar propósito, código, alternativas y verificación durante propuestas, preguntas, decisiones, implementación y resúmenes, con nivel de estudiante principiante en FastAPI. Changes de tamaño habitual por cohesión técnica; no fragmentarlos artificialmente.
15. **Git y ejecución:** no commit/push sin pedido explícito. Ejecutar pruebas y comprobaciones de build correspondientes al trabajo autorizado; no introducir confirmaciones repetidas para esa verificación.

### Gobernanza del usuario

| Nivel | Dominios | Acción |
|---|---|---|
| BAJO | CRUD simple, tipos, utilidades de lectura | Autonomía; verificar y resumir |
| MEDIO | Lógica de negocio, sesiones y pipelines | Implementar con checkpoints y explicar decisiones no obvias |
| ALTO | Configuración que afecta datos/VPS, backup/restore, dotfiles | Preparar propuesta concreta y esperar revisión antes de cambios en ese entorno |
| CRÍTICO | Auth, pagos, seguridad, auditoría | Análisis; no código sin aprobación explícita |

La venta de este parcial no procesa pagos ni constituye billing. Antes de publicar, inspeccionar servicios/puertos/base y preparar comandos concretos para revisar; preservar el otro proyecto de la VPS. Una autorización ya otorgada para una acción no requiere repetir la misma pregunta.

### Strict TDD durante implementación

- Si se modifican archivos existentes, ejecutar pruebas relevantes primero y registrar baseline; ante falla previa, detener esa tarea e informar sin repararla por cuenta propia.
- Preparar el runner si aún falta. Antes de código productivo, escribir una prueba conductual que falle y ejecutar RED por la razón esperada.
- Implementar el mínimo, ejecutar y confirmar GREEN. Triangular con al menos dos casos distintos por comportamiento, incluido un borde, hasta cubrir escenarios.
- Refactorizar sólo con pruebas verdes, ejecutándolas tras cada refactor. Evitar tautologías y pruebas que sólo reflejen la implementación.
- Marcar tasks completas únicamente tras verificación. La documentación reversible no requiere tests artificiales.
- Incluir tabla de evidencia con columnas: Task, Test File, Layer, Safety Net, RED, GREEN, TRIANGULATE, REFACTOR.

## Flujo de Trabajo

1. Consultar KB y CHANGES para el alcance; recuperar contexto de Engram. Explicar el objetivo y las decisiones que se proponen.
2. Consultar `openspec list --json`; para un change existente, `openspec status --change "<nombre>" --json` antes de actuar. Usar `openspec instructions` y la skill de la acción; no inferir estado por memoria.
3. Proponer con `openspec-propose`; explorar con `openspec-explore` si hace falta pensar sin implementar. El CLI crea estructura y metadatos: nunca armar openspec/ manualmente.
4. Implementar con `openspec-apply-change` y reglas resueltas del registro. Validar cada comportamiento con TDD; explicar resultados y límites.
5. Sincronizar/archivar con la skill correspondiente cuando esté completado y verificado; marcar el índice CHANGES sólo por trabajo realmente terminado. OPSX admite revisar acciones sin fase gates rígidos.
6. Mantener contexto persistente y resumir el resultado. No iniciar publicación, merge, envío al campus ni comunicaciones a terceros por completar tareas locales.

### Delegación — sólo para el coordinador

- Delegar exploración de cuatro o más archivos, análisis/escritura multifile y ejecución de tests/builds. Lecturas cortas para decidir, estado CLI/Git y ediciones mecánicas de un archivo pueden resolverse inline.
- Usar agentes internos para subtareas; no crear chats del usuario ni asignarles tecnologías ajenas al alcance.
- Pasar objetivo, change, contexto recuperado, archivos y `## Project Standards (auto-resolved)` con los bloques pertinentes del registro. Si falta, self-resolve desde fuentes disponibles.
- Los ejecutores implementan su tarea y devuelven evidencia/decisiones; no heredan la obligación de delegar todo como un coordinador ni repiten preguntas ya resueltas.

### Engram y continuidad

- Al iniciar, usar mem_context y mem_search con "opsx" y el proyecto detectado desde cwd; recuperar observaciones completas si hace falta. El proyecto de memoria actual es "parcial 2".
- Guardar decisiones, fixes, patrones, elecciones de herramientas, configuración y hallazgos importantes inmediatamente con mem_save, topic_key estable y formato What/Why/Where/Learned. Tras una acción OPSX, guardar acción/change/archivos/próximo paso.
- Antes de cerrar la sesión, usar mem_session_summary con Goal, Instructions, Discoveries, Accomplished, Next Steps y Relevant Files.
- Tras compacción, persistir inmediatamente el resumen compactado con mem_session_summary, recuperar mem_context y sólo después continuar.
- Si se versiona .engram/, exportar memoria de este proyecto antes de push e importar después de clone/pull. Nunca engram sync --all; revisar visibilidad antes de versionar memoria en repo público.
- Si una herramienta no está disponible, informar la limitación y conservar el contexto en artefactos reales sin afirmar persistencia o verificación inexistente.

Las decisiones posteriores del usuario prevalecen. Ante diferencias entre fuentes, señalar el conflicto y actualizar la documentación pertinente sin atribuir al PDF reglas que no contiene.
