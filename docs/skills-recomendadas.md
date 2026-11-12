# Skills recomendadas para totones

Evaluación del 11 de noviembre de 2026 para la API de librería de Programación III, 2PRO1. Estado actual verificado el **11 de noviembre de 2026**: **ambas skills aprobadas e instaladas sólo a nivel proyecto**, con copia para Codex en `.agents/skills/`. La evaluación inicial fue de recomendaciones; la decisión posterior del usuario autorizó estas dos instalaciones y la fase registry.

Una skill es una guía de instrucciones para el agente. No es una dependencia que ejecute la API: instalar una skill de pytest no instala pytest, y una guía publicada por Supabase no obliga a usar su plataforma. La consigna, la KB y las instrucciones del grupo mantienen precedencia.

## Procedimiento de evaluación inicial (histórico)

- Leí la skill local find-skill y revisé primero el [leaderboard de skills.sh](https://www.skills.sh/).
- Inspeccioné en lectura los directorios de skills globales de .agents/.codex y los del proyecto. En esa evaluación aún no estaban instaladas las dos recomendaciones. Después se instalaron localmente por autorización del usuario; sus archivos SKILL.md están registrados por ruta en `.atl/skill-registry.md`.
- No había ejecutable skills ni paquete skills en el caché _npx inspeccionado. Usé búsqueda web y archivos de los repositorios; durante esa evaluación no ejecuté npx ni descargué/ejecuté código de los candidatos. La instalación autorizada posterior sí usó la CLI indicada abajo.
- Busqué FastAPI/SQLAlchemy async/SQLModel, pytest/TDD, PostgreSQL y Docker/despliegue. Revisé SKILL.md y las referencias pertinentes de los candidatos seleccionados antes de recomendar.
- Las instalaciones son cifras aproximadas mostradas por skills.sh; las estrellas son cifras redondeadas observadas en GitHub. Son señales de adopción, no pruebas de calidad. Pueden cambiar y las páginas consultadas pueden tener cachés diferentes.

## Recomendaciones

| Skill | Repositorio y procedencia | Instalaciones observadas | Estrellas observadas | Aporte concreto |
|---|---|---:|---:|---|
| python-testing-patterns | [wshobson/agents](https://github.com/wshobson/agents), comunidad | aprox. 40,1 mil | aprox. 42,4 mil | Fixtures, parametrización, excepciones y pruebas async para los changes C-01 a C-06 |
| supabase-postgres-best-practices | [supabase/agent-skills](https://github.com/supabase/agent-skills), mantenida por Supabase | aprox. 481,6 mil | aprox. 3 mil | Diseño relacional, índices de FK y prevención de N+1, especialmente C-02 a C-06 |

### python-testing-patterns

Revisé el [SKILL.md actual](https://github.com/wshobson/agents/blob/main/plugins/python-development/skills/python-testing-patterns/SKILL.md) y su [referencia avanzada](https://github.com/wshobson/agents/blob/main/plugins/python-development/skills/python-testing-patterns/references/advanced-patterns.md). Aporta patrones pytest para preparar datos, probar variantes y comprobar errores/concurrencia; complementa Strict TDD ya requerido, sin sustituirlo. [Ficha y cifra de instalaciones](https://www.skills.sh/wshobson/agents/python-testing-patterns).

Aplicación acotada: usar sólo patrones necesarios para comportamientos reales. Sus ejemplos de fallback SQLite, limpieza automática de una DB, tokens y umbrales de cobertura no se incorporan como requisitos. La integración de esta API se verifica con PostgreSQL aislado, DATABASE_URL sin valor por defecto y sin borrar datos reales. No exige repositorios, auth, Alembic ni Compose. Los .http y evidencias del parcial siguen siendo obligatorios. No agregar herramientas auxiliares sólo porque aparezcan en ejemplos.

Comando ejecutado tras la autorización del usuario, **sólo a nivel proyecto**:

```powershell
npx skills add https://github.com/wshobson/agents --skill python-testing-patterns --agent codex --copy --yes
```

### supabase-postgres-best-practices

El [SKILL.md actual](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/SKILL.md) declara aplicabilidad a PostgreSQL en cualquier entorno. Revisé las reglas de [índices en FK](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/references/schema-foreign-key-indexes.md) y [carga agrupada para N+1](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/references/data-n-plus-one.md). Son pertinentes para justificar el esquema y comprobar consultas. [Ficha y cifra de instalaciones](https://www.skills.sh/supabase/agent-skills/supabase-postgres-best-practices).

Aplicación acotada: esquema, índices, consultas y conexiones en el dominio existente. RLS, auth, migraciones, extensiones y servicios de Supabase son categorías contextuales; la skill no exige activarlas universalmente ni contratar su plataforma. Mantener SQLModel, SQLAlchemy async, create_all y joinedload/selectinload del parcial. Sus prioridades de impacto no reemplazan los niveles de gobernanza del usuario. La guía no autoriza cambios de configuración ni operaciones sobre la VPS; esas acciones requieren la revisión concreta ya prevista.

Comando ejecutado tras la autorización del usuario, **sólo a nivel proyecto**:

```powershell
npx skills add https://github.com/supabase/agent-skills --skill supabase-postgres-best-practices --agent codex --copy --yes
```

## Candidatas evaluadas que no se recomiendan en esta selección

| Candidata | Adopción observada | Motivo concreto |
|---|---|---|
| [fastapi, fastapi/fastapi](https://www.skills.sh/fastapi/fastapi/fastapi) | 15 mil instalaciones; GitHub aprox. 104,7 mil estrellas | La fuente es el repositorio oficial y hay consejos útiles de tipado/Depends. Sin embargo, sus defaults y herramientas adicionales requieren filtrar varios desajustes con este parcial; se documentan abajo. |
| [fastapi-templates, wshobson/agents](https://www.skills.sh/wshobson/agents/fastapi-templates) | 26,5 mil instalaciones; repo aprox. 42,4 mil estrellas | La ficha propone layout con repositories, repositorio genérico y auth JWT. Su arquitectura de ejemplo requeriría adaptación importante a la organización modular del PDF; no se afirma que esos extras sean una obligación universal. La evaluación se limita a la ficha y su SKILL.md visible allí. |
| [docker-expert, sickn33/agentic-awesome-skills](https://www.skills.sh/sickn33/agentic-awesome-skills/docker-expert) | 27,4 mil instalaciones; repo aprox. 49,5 mil estrellas | El archivo real contiene ejemplos Node/Compose, una comprobación compose en su flujo y una regla que evita secretos en variables de entorno. El parcial exige Python Alpine, docker run y --env-file. Su alcance general suma más adaptación que ayuda en esta selección. |
| [test-driven-development, obra/superpowers](https://www.skills.sh/obra/superpowers/test-driven-development) | 276,5 mil instalaciones; 315,7 mil estrellas mostradas por la ficha, no contrastadas con GitHub en esta evaluación | El [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md) explica RED/GREEN/refactor; no se selecciona por redundancia con Strict TDD explícito del usuario. La skill pytest aporta patrones de implementación que ese protocolo no detalla. |

La [skill oficial FastAPI inspeccionada](https://github.com/fastapi/fastapi/blob/master/fastapi/.agents/skills/fastapi/SKILL.md) prefiere def por defecto cuando hay dudas y Asyncer sobre asyncio; también presenta CLI/Cloud, frontend y telemetría. Cloud es una sección contextual, no una obligación universal. No observé un helper/script de despliegue ejecutado automáticamente en el SKILL.md; sí comandos sugeridos que no ejecuté. Para este proyecto se conservarán handlers async, asyncio.sleep, uvicorn y VPS, usando documentación oficial según corresponda.

Además, la [auditoría externa publicada en skills.sh](https://www.skills.sh/fastapi/fastapi/fastapi/security/agent-trust-hub), fechada 8 de noviembre de 2026, muestra Fail y objeta las referencias Cloud. Es una evaluación externa: no la presento como prueba de que el repositorio oficial sea malicioso ni como un hallazgo resuelto. Esta selección evita introducir esa guía de alcance más amplio.

El [SKILL.md de Docker revisado](https://github.com/sickn33/agentic-awesome-skills/blob/main/skills/docker-expert/SKILL.md) contiene buenas prácticas de capas, exclusiones y usuario no root; no se selecciona por los desajustes indicados. Esto no cambia los requisitos Docker de CHANGES.md ni impide implementarlos con su documentación oficial.

No se añade una skill específica de SQLModel/SQLAlchemy async por completar una lista. El contrato del parcial ya fija sesión, precarga y modelos; se consultará documentación primaria durante los changes correspondientes.

## Decisión aplicada y verificación local

El usuario eligió ambas skills y autorizó instalarlas **únicamente en este proyecto**. No se hicieron instalaciones globales de estas skills. La instalación de guías no instala dependencias Python ni habilita implementación, VPS o cambios fuera del alcance aprobado.

| Skill | Ruta local | Origen registrado | Estado comprobado |
|---|---|---|---|
| python-testing-patterns | `.agents/skills/python-testing-patterns/SKILL.md` | wshobson/agents | project / tracked / copy |
| supabase-postgres-best-practices | `.agents/skills/supabase-postgres-best-practices/SKILL.md` | supabase/agent-skills | project / tracked / copy |

Verificación: **2026-11-11**. La CLI de skills confirmó `scope: project` y estado `tracked`; los archivos existen en las rutas indicadas. `skills-lock.json` versión 2 registra source, skillPath, installMode y computedHash. `.active-orchestrator-state.json` conserva las dos instalaciones en `skills.installed`; `.atl/skill-registry.md` incorpora triggers, rutas y reglas compactas con límites del parcial.

| Skill | computedHash del lock |
|---|---|
| python-testing-patterns | `8113c05a831d4872c9294b0df26a335c09af423ee2e23d8b9b6817b300d96796` |
| supabase-postgres-best-practices | `3eb972c2d7c818e544e35cc33ea8d7147d4d78ae08142ef40037b0fbac7a2505` |

La evaluación y fuentes anteriores se conservan como historia de la selección. La fase registry ya genera el catálogo; la fase posterior `agent-instruction` requiere su checkpoint y confirmación de reglas. No se inicia implementación por completar este registro.
