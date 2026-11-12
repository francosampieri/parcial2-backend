# Librería — Base de conocimiento

Documentación generada por ingesta de la consigna académica y del contexto aportado por el grupo. Estado: requisitos documentados; API y despliegue pendientes.

## Fuentes y precedencia

- [Consigna original](../docs/consigna-parcial.pdf): 16 páginas, unidades 1 a 4 de Programación III. Define requisitos del parcial, ejercicios, casos y evaluación.
- [Contexto del grupo](../docs/contexto-del-grupo.md): totones, de 2PRO1; Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria; acompañamiento didáctico, OpenSpec/TDD y VPS existente. Entrega: `Parcial_Cap1a4_totones.zip`.
- Las propuestas y dudas se identifican en los documentos 09 y 10. Un ejemplo del PDF no fija datos reales del despliegue ni una fecha de entrega.

## Índice de archivos

| Archivo | Contenido |
|---|---|
| [01 — Visión y objetivos](01_vision_y_objetivos.md) | Alcance, objetivos y evaluación |
| [02 — Descripción general](02_descripcion_general.md) | Stack mínimo, arquitectura e integraciones |
| [03 — Actores y roles](03_actores_y_roles.md) | Actores y acceso público, sin RBAC |
| [04 — Modelo de datos](04_modelo_de_datos.md) | Nueve tablas, relaciones, restricciones y seed |
| [05 — Reglas de negocio](05_reglas_de_negocio.md) | RN-01 a RN-12 y contratos complementarios |
| [06 — Funcionalidades](06_funcionalidades.md) | Historias, 26 operaciones HTTP y aceptación |
| [07 — Flujos principales](07_flujos_principales.md) | Arranque, altas, lecturas, ventas y publicación |
| [08 — Arquitectura propuesta](08_arquitectura_propuesta.md) | Estructura, sesiones, configuración, Docker y pruebas |
| [09 — Decisiones y supuestos](09_decisiones_y_supuestos.md) | Mandatos del PDF, decisiones del usuario y propuestas |
| [10 — Preguntas abiertas](10_preguntas_abiertas.md) | Dudas priorizadas y diferencias entre fuentes |

## Lectura inicial para desarrollar

1. Entender el objetivo y los actores: documentos 01 y 03.
2. Entender entidades y reglas: documentos 04 y 05.
3. Revisar estructura y contratos: documentos 02, 06 y 08.
4. Seguir los flujos del documento 07 y revisar dudas del 10 antes de implementar.
5. Usar el documento 09 para distinguir obligaciones de elecciones todavía revisables.

## Resumen ejecutivo

API REST asincrónica de catálogo y ventas de una librería, con FastAPI, SQLModel y PostgreSQL. La API se empaqueta en una imagen Docker y se publica en una instancia accesible en VPS; se entregan el código y el Dockerfile, junto con pruebas `.http`, documentación y evidencias reales. El desarrollo se organizará en changes del tamaño habitual según su cohesión técnica, sin fragmentación artificial, con TDD por instrucción del usuario. El acompañamiento didáctico estará presente en propuestas, preguntas, decisiones, resúmenes e implementación, además de explicar el código y su verificación.
