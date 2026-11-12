# Preguntas abiertas

Las dudas se registran sin bloquear la generación de la KB. Se resuelven antes del change al que afectan; no hace falta responderlas todas para iniciar el desarrollo local.

## Inconsistencias detectadas

### IN-01 — Destino del despliegue

**Documento A dice**: la cátedra provee VPS, datos de acceso y base.
**Documento B dice**: el usuario tiene una VPS hace meses y ya aloja otro proyecto.
**Impacto**: elegir un destino/base/puerto incompatible o afectar el proyecto existente.
**Resolución propuesta**: confirmar si es el mismo servidor y qué entorno permite la evaluación. Luego revisar servicios, red y base disponibles sin alterar el otro proyecto.

### IN-02 — Paginación resumida en tablas de rutas

**Documento A dice**: RN-10 exige paginación para todo listado.
**Documento B dice**: algunas filas de endpoints de referencia no muestran limit/offset.
**Impacto**: implementar rutas relacionadas sin paginación.
**Resolución propuesta**: aplicar RN-10 en todos los listados; omisión de la tabla tomada como resumen, no excepción.

### IN-03 — Autoría mínima en diagrama y tabla

**Documento A dice**: figura 1 representa uno o varios autores para un libro.
**Documento B dice**: tabla relacional/alta lista autores sin precisar en texto su longitud mínima.
**Impacto**: permitir un libro sin autorías pese al modelo conceptual.
**Resolución propuesta**: proponer mínimo una autoría en LibroCreate y explicitarlo en el diseño. No presentar una validación textual inexistente como cita del PDF.

## Preguntas abiertas priorizadas

| ID | Prioridad | Pregunta | Bloquea | Decisor |
|---|---|---|---|---|
| PA-01 | Alta antes de despliegue | ¿La VPS existente es la asignada/autorizada por la cátedra y qué PostgreSQL/base/usuario se deben usar? | Configuración real de despliegue | Grupo/cátedra |
| PA-02 | Alta antes de despliegue | ¿Qué puerto/URL pública usará el parcial y qué servicios, contenedores y proxy están activos? | Publicación sin interferir proyecto existente | Grupo/administrador VPS |
| PA-03 | Alta en entorno inicial | ¿Están disponibles Python 3.12+, PostgreSQL 16 y Docker, y qué DB aislada se usará para pruebas? | Ejecución de integración y Docker; se puede inspeccionar primero | Equipo |
| PA-04 | Media, antes de contratos | ¿PATCH libro modifica autorías o sólo atributos simples/referencias? Si modifica lista, ¿cómo la reemplaza? | Diseño LibroUpdate y pruebas | Equipo; cátedra si hay aclaración |
| PA-05 | Media, antes de contratos | ¿Qué campos admiten NULL explícito en PATCH? ¿Qué reglas adicionales de texto/email se adoptan sin exceder el alcance? | DTO Update y respuestas 422/409 coherentes | Equipo |
| PA-06 | Media, antes de seed | ¿Cómo repetir el seed preservando datos y manteniendo IDs usados por casos? | Seed reproducible y D-03 | Equipo |
| PA-07 | Media, antes de salud | ¿Se adopta ready 503 con mensaje propio cuando DB cae después del arranque? | Contrato de error de salud | Equipo |
| PA-09 | Media para planificación | ¿Qué fecha y hora límite publicó el campus? | Planificación de entrega | Grupo/campus |
| PA-10 | Baja | ¿Hay alguna aclaración de cátedra sobre inventario o sobre mínimo de autorías? | Sólo comportamiento adicional si existe aclaración | Grupo/cátedra |
| PA-11 | Baja | ¿Se exige orden concreto de listados o formato de errores aparte de mensajes propios? | Afinar contratos; proponer orden estable | Equipo |
| PA-12 | Baja | ¿Se conocen volúmenes o concurrencia esperados más allá de evaluación grupal? | Confirmación de escala; no bloquea API académica | Grupo/cátedra |

## Incertidumbres de discovery inferido

[DISCOVERY] scale no está especificado con confianza en los documentos fuente. Se registra como **team (inferred, low confidence)** por el contexto de entrega grupal de totones, con cuatro integrantes confirmados. Esto describe el proyecto académico, no restringe la cantidad de usuarios de la API ni agrega autenticación. Confirmar si existe exigencia de volumen o concurrencia.

Los otros campos se infieren con confianza: system_type=api, domain=librería (catálogo y ventas), needs_infra=true y stack indicado en el documento 02.

## Aclaraciones ya resueltas

- PA-08 resuelta por el usuario: grupo **totones**, integrado por **Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria**, de **2PRO1**. ZIP: **Parcial_Cap1a4_totones.zip**.
- Discovery opcional de producto/mercado omitido por elección expresa del usuario.
- El límite <100 MB es para python:3.12-alpine como imagen base, no para la imagen final.
- La fecha 2026-10-08 del ejemplo JSON y la medición Docker de noviembre son ejemplos, no plazos de entrega.
- TDD/OpenSpec son instrucciones del usuario; la consigna exige .http y evidencias.
- No asumir descuento de stock ni consultas previas de unicidad.
- No completar URL/fecha de DEPLOY ni evidencias D con valores inventados.

## Fuente

Consigna completa y contexto del grupo. Estas preguntas distinguen requisitos faltantes de decisiones técnicas rutinarias que pueden proponerse al diseñar cada change.
