# Contexto aportado por el grupo

Fuente: mensajes del usuario del 11 de noviembre de 2026. Este archivo distingue sus pedidos de las consignas académicas de `consigna-parcial.pdf`.

- Grupo: totones.
- Integrantes: Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria.
- Curso: 2PRO1. Materia: Programación III.
- Objetivo: desarrollar la API completa del parcial y luego recibir guía para publicarla en la VPS.
- Aprendizaje: Franco conoce programación y conceptos muy básicos de FastAPI. Incluir explicaciones didácticas al proponer, preguntar, decidir, resumir e implementar: explicar el propósito, los conceptos nuevos, sus consecuencias y cómo verificar lo construido, no sólo el código.
- Tamaño de los changes: usar el tamaño habitual según la cohesión técnica del trabajo. No fragmentar artificialmente para hacerlos pequeños; el acompañamiento didáctico no requiere reducir su alcance.
- Infraestructura: el grupo tiene una VPS desde hace meses y ya aloja un proyecto pequeño. Conocen algunos conceptos de DevOps aprendidos durante ese despliegue. Revisar cómo convivirán los proyectos antes de publicar.
- Flujo elegido: active-orchestrator para la fundación; luego changes con OpenSpec. El usuario eligió continuar a la KB sin Discovery.
- Las instrucciones del usuario habilitan Strict TDD en implementación cuando haya un test runner. Esta metodología es una instrucción de trabajo; el PDF exige los archivos `.http` y las evidencias indicadas, sin exigir TDD.
- Reglas de implementación confirmadas al generar AGENTS.md/CLAUDE.md: (1) snake_case en funciones/variables y anotaciones de tipos en funciones y contratos Python, conservando nombres obligatorios de tablas/columnas; (2) `extra='forbid'` en DTO de entrada, incluidos Create, Update y entradas anidadas, para rechazar campos no declarados con 422; (3) altas compuestas atómicas de libro con autorías y venta con renglones, con rollback completo si falla alguna parte. Son decisiones aprobadas por el usuario; la política de campos extra no se atribuye textualmente al PDF.
- El usuario aprobó primero las reglas 1 y 3 y luego confirmó la regla 2 con «me parece bien, incorporala», tras explicar el ejemplo de cliente con nombre/email y un campo edad extra que produciría 422. Esta aprobación no resuelve qué campos de PATCH admiten NULL, cómo se actualizan autorías, la política de seed, el contrato ready 503 ni el orden/mínimo de autorías: esas decisiones siguen para sus changes.
- Respetar los checkpoints de la skill entre fases. No instalar skills globales sin elección del usuario.
- Nombre de entrega confirmado: `Parcial_Cap1a4_totones.zip`. La fecha límite sigue pendiente de consulta en campus.
- No se proporcionaron acceso, puertos, dominio ni credenciales de VPS/base. No inventarlos ni guardarlos en documentación versionable.

El PDF define el producto académico. Sus ejemplos de comandos describen requisitos de entrega; no constituyen autorización para ejecutar comandos sobre el proyecto que ya está alojado.
