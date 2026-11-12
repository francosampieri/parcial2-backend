# Visión y objetivos

## Propósito del sistema

Gestionar mediante una API el catálogo, los clientes y las ventas de una librería de barrio, demostrando los contenidos de los capítulos 1 a 4 de Programación III y su despliegue en VPS.

El parcial integra contratos HTTP, ejecución asincrónica y persistencia relacional. Debe permitir explicar por qué cada relación tiene sus claves foráneas, cómo se evitan consultas N+1 y cómo corre el mismo código dentro de Docker.

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| Operador de librería | Administrar catálogo y registrar ventas | Consultar autores, editoriales, géneros, clientes y precios históricos |
| Grupo desarrollador | Entregar y comprender una API que cumpla la consigna | Aprender FastAPI, relaciones, pruebas y despliegue |
| Cátedra | Verificar los contenidos y casos exigidos | Probar la URL pública y revisar código, documentación y evidencias |

Grupo aportado por el usuario: **totones**, de **2PRO1**. Integrantes: **Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria**.

## Alcance v1.0

- API asincrónica con los módulos `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes` y `ventas`.
- Catálogo con editorial existente, género opcional y autorías con rol y orden.
- Clientes con un perfil opcional como máximo.
- Ventas con renglones anidados, copia de precios y total calculado por el servidor.
- Contratos separados de tablas, validaciones, PATCH parcial y listados paginados.
- Persistencia PostgreSQL con restricciones e índices, carga anticipada y errores propios.
- Ciclo de vida con creación de tablas faltantes y dos rutas de salud.
- Aviso de comprobante simulado en segundo plano, después de responder.
- Datos iniciales reproducibles, archivos `.http`, evidencia C-07 y D-01 a D-07.
- Imagen Docker, publicación en VPS, README, DEPLOY y ZIP de entrega.
- Acompañamiento didáctico en propuestas, preguntas, decisiones, resúmenes e implementación, por pedido del usuario; explicar conceptos, propósito y verificación.
- Changes del tamaño habitual según su cohesión técnica, sin fragmentación artificial por motivos pedagógicos.

## Fuera de alcance

El PDF indica que no se evalúan autenticación/autorización, repositorios, Unit of Work, Redis/colas ni migraciones. Se mantiene la arquitectura indicada por módulo. El despliegue exigido usa `docker run`, sin Compose y con PostgreSQL fuera del contenedor de aplicación.

No se solicita frontend, pagos, facturación real, envío real de correo, DELETE, edición de ventas, alta independiente de renglones, descuento automático de stock ni reservas. Cualquier ampliación debe identificarse como tal antes de incorporarse.

## Métricas de éxito

| Criterio de la consigna | Peso |
|---|---:|
| Proyecto, conexión y ciclo de vida | 8% |
| Modelos, restricciones y relaciones | 22% |
| Contratos y CRUD | 12% |
| Altas con relaciones | 17% |
| Lecturas sin N+1 | 8% |
| Asincronía sin bloqueos | 8% |
| Contenedor: imagen | 15% |
| Despliegue en VPS | 10% |

Se deben demostrar C-01 a C-08 y D-01 a D-07. El proyecto debe arrancar y crear el esquema sobre una base vacía. No debe contener credenciales reales en código, repositorio, imagen ni ZIP. La instancia debe permanecer accesible hasta la publicación de notas.

La entrega es una por grupo: `Parcial_Cap1a4_<NombreDelGrupo>.zip`, con una sola carpeta de proyecto. Para este grupo, el nombre confirmado es `Parcial_Cap1a4_totones.zip`. La fecha límite se consulta en campus.

## Fuente

Consigna: páginas 1–3 y 14–16. Contexto del grupo: `docs/contexto-del-grupo.md`.
