# Actores y roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|---|---|---|
| Operador de la librería | Usuario funcional del catálogo y las ventas | Peticiones HTTP; no se solicita interfaz gráfica |
| Cliente registrado | Entidad que participa en ventas y puede tener perfil | Su información la administra la API; no tiene login |
| Grupo desarrollador | totones: Franco Sampieri, Mauro Di Pietro, Tomas Martinez y Renzo Victoria; 2PRO1 | Implementa, prueba, documenta y publica |
| Cátedra | Evalúa el parcial | Ejecuta casos, revisa ZIP y accede a URL pública |
| Administrador de VPS | Opera infraestructura | Prepara variables, red y contenedor; identidad/acceso pendientes |

## RBAC — Matriz de permisos

**No aplica RBAC en este parcial.** La consigna deja autenticación y autorización fuera de evaluación. Los actores anteriores describen responsabilidades, no roles implementados ni niveles de acceso.

| Consumidor HTTP | Recursos | Operaciones disponibles |
|---|---|---|
| Cualquier consumidor con acceso de red | Salud | Consultar live/ready |
| Cualquier consumidor con acceso de red | Catálogo | Operaciones de alta, lectura y PATCH definidas |
| Cualquier consumidor con acceso de red | Clientes/perfiles | Alta, lectura y PATCH según endpoint |
| Cualquier consumidor con acceso de red | Ventas | Alta y lectura; sin PATCH |

Que un cliente sea un registro en la base no le asigna permisos ni lo convierte en usuario autenticado.

## Rutas públicas

Todas las rutas del inventario de [06](06_funcionalidades.md) son públicas: `/health/live`, `/health/ready` y las operaciones definidas bajo `/editoriales`, `/generos`, `/autores`, `/libros`, `/clientes` y `/ventas`.

Las credenciales PostgreSQL son configuración de infraestructura. No se entregan a consumidores HTTP ni aparecen en respuestas, README, evidencias o imagen.

## Fuente

Consigna: páginas 2 y 11–14. Integrantes y experiencia: contexto del usuario.
