# Funcionalidades

## Inventario de endpoints

Las 26 operaciones de referencia se conservan. Los códigos generales 404/409/422 se aplican según el caso aunque alguna fila del PDF los omita. Cada listado admite limit=20 (1–100) y offset=0 (>= 0), por RN-10.

| Método | Ruta | Entrada / salida principal |
|---|---|---|
| GET | /health/live | Sin DB; {"estado":"vivo"} |
| GET | /health/ready | Ejecuta SELECT 1; estado de DB |
| POST | /editoriales/ | EditorialCreate → EditorialRead, 201 |
| GET | /editoriales/ | Lista paginada de EditorialRead |
| GET | /editoriales/{id} | EditorialRead o 404 |
| PATCH | /editoriales/{id} | EditorialUpdate parcial → EditorialRead |
| GET | /editoriales/{id}/libros | Lista paginada de libros; editorial inexistente 404 |
| POST | /generos/ | GeneroCreate → GeneroRead, 201 |
| GET | /generos/ | Lista paginada de GeneroRead |
| GET | /generos/{id}/libros | Lista paginada; género inexistente 404 |
| POST | /autores/ | AutorCreate → AutorRead, 201 |
| GET | /autores/{id} | AutorRead o 404 |
| PATCH | /autores/{id} | AutorUpdate parcial → AutorRead |
| GET | /autores/{id}/libros | Lista paginada de libros con rol y orden |
| POST | /libros/ | LibroCreate con autorías → detalle, 201 |
| GET | /libros/ | Lista con editorial/género; filtros titulo y genero_id |
| GET | /libros/{id} | Libro con editorial, género y autores |
| PATCH | /libros/{id} | LibroUpdate parcial → detalle |
| POST | /clientes/ | ClienteCreate → ClienteRead, 201 |
| GET | /clientes/{id} | Cliente con perfil opcional |
| PATCH | /clientes/{id} | ClienteUpdate parcial → cliente con perfil |
| POST | /clientes/{id}/perfil | PerfilCreate → PerfilRead, 201; 404/409 |
| GET | /clientes/{id}/ventas | Lista paginada; cliente inexistente 404 |
| POST | /ventas/ | VentaCreate con renglones → detalle, 201 |
| GET | /ventas/ | Lista paginada de ventas |
| GET | /ventas/{id} | Venta con cliente y renglones |

No agregar por defecto CRUD completo a todos los recursos. El PDF no pide DELETE, PATCH ventas ni POST renglones independientes.

## Épica 1: Aplicación y salud

### US-001 — Iniciar una aplicación conectada

**Como** desarrollador/evaluador, **quiero** iniciar la API desde una base vacía, **para** disponer de un servicio verificable sin crear tablas a mano.

**Criterios de aceptación**:

- [ ] Motor y fábrica de sesiones se crean en lifespan y se guardan en app.state.
- [ ] Todos los modelos se importan antes de create_all; sólo se crean tablas faltantes.
- [ ] Una sesión por petición con Depends y expire_on_commit=False; motor dispuesto al apagar.
- [ ] Live responde 200 con estado vivo sin consulta DB; ready ejecuta SELECT 1.
- [ ] Falta de DATABASE_URL o DB inaccesible impide completar arranque.

**Reglas relacionadas**: RT-CFG-01, RT-ASYNC-01. Ejercicio 1; D-02 y D-05.

## Épica 2: Catálogo

### US-002 — Administrar referencias de catálogo

**Como** operador, **quiero** dar de alta y consultar editoriales, géneros y autores, **para** utilizarlos al registrar libros.

**Criterios de aceptación**:

- [ ] Están disponibles las rutas de referencia y sus PATCH indicados.
- [ ] Nombres únicos de editorial/género protegidos por DB; conflictos con mensaje propio.
- [ ] Rutas con ID inexistente devuelven 404; ID no entero, 422.
- [ ] Listados relacionados paginados; autor/libros muestra rol y orden.

**Reglas relacionadas**: RN-10, RN-12, RT-CAT-05, RT-HTTP-01. Ejercicios 2 y 3; C-01.

### US-003 — Registrar y consultar libros con autorías

**Como** operador, **quiero** registrar libros mediante IDs de referencias existentes y datos de autoría, **para** representar editorial, género opcional y participación de autores.

**Criterios de aceptación**:

- [ ] Alta recibe isbn, titulo, precio, stock, editorial_id, genero_id opcional y autores con autor_id/rol/orden.
- [ ] No se preconsulta existencia de IDs ni unicidad; se escribe y traduce IntegrityError.
- [ ] DTO inválido → 422; ISBN repetido o FK inexistente → 409 propio.
- [ ] Detalle devuelve editorial, género y autorías con datos de autor.
- [ ] Listado devuelve editorial/género, pagina y filtra por título parcial sin distinguir mayúsculas y por género.
- [ ] Búsqueda ' OR '1'='1 usa parámetros ligados y devuelve 200 con lista vacía sobre seed conocido.
- [ ] PATCH preserva campos omitidos; semántica de modificación de autorías pendiente de explicitar.

**Reglas relacionadas**: RN-01, RN-03, RN-10, RN-11, RN-12, RT-CAT-01 a 04. Ejercicios 2–5; C-02, C-04, C-08.

## Épica 3: Clientes

### US-004 — Registrar clientes y perfil único

**Como** operador, **quiero** registrar clientes y su perfil opcional, **para** asociar ventas y datos de contacto.

**Criterios de aceptación**:

- [ ] Alta/lectura/PATCH cliente con contratos separados; email único en DB.
- [ ] El perfil se crea para cliente existente; segundo perfil → 409, cliente inexistente → 404.
- [ ] La lectura de cliente devuelve perfil como objeto opcional con precarga.
- [ ] Las ventas del cliente se consultan paginadas.

**Reglas relacionadas**: RN-02, RN-09, RN-10, RN-12. C-02 y C-03.

## Épica 4: Ventas

### US-005 — Registrar una venta completa

**Como** operador, **quiero** enviar cliente y renglones en una sola petición, **para** guardar una venta con precios históricos y total consistente.

**Criterios de aceptación**:

- [ ] Entrada contiene cliente_id y renglones sólo con libro_id/cantidad.
- [ ] Renglones vacíos, libros repetidos o cantidades inválidas → 422.
- [ ] Cliente/libro inexistente → 409; no se confirma una venta parcial.
- [ ] Se copian precios de DB; fecha y total se calculan en servidor con Decimal.
- [ ] Respuesta 201 incluye cliente y renglones con título, precio unitario y subtotal.
- [ ] Cambiar después el precio del libro no cambia el precio histórico del renglón.
- [ ] Se puede listar y consultar venta; no editarla ni crear renglones sueltos.

**Reglas relacionadas**: RN-04 a RN-08, RT-VTA-01 a 03. Ejercicio 4; C-05, C-06, D-03.

### US-006 — Avisar sin bloquear la API

**Como** operador, **quiero** obtener la respuesta antes del aviso simulado, **para** que el servicio siga atendiendo mientras se procesa el comprobante.

**Criterios de aceptación**:

- [ ] BackgroundTasks agenda una función async con await asyncio.sleep(0.5).
- [ ] El mensaje aparece en log después de la línea de respuesta.
- [ ] No hay time.sleep, requests ni operaciones DB síncronas en handlers.

**Reglas relacionadas**: RT-VTA-04, RT-ASYNC-01. Ejercicio 6; D-07.

## Épica 5: Verificación y entrega

### US-007 — Demostrar relaciones y consultas acotadas

**Como** evaluador, **quiero** ejecutar casos reproducibles, **para** comprobar reglas, errores y ausencia de N+1.

**Criterios de aceptación**:

- [ ] Script/comando de seed y casos .http C-01 a C-08 con respuesta esperada en comentario.
- [ ] Detalle libro/venta con consultas fijas para uno y varios autores/renglones.
- [ ] Log SQL configurable y evidencia C-07 guardada sin secretos.
- [ ] TDD de implementación con runner disponible, además de los entregables .http del PDF.

**Reglas relacionadas**: RT-DB-02 y 03. Ejercicio 5; instrucciones de trabajo del usuario para TDD.

### US-008 — Publicar y entregar

**Como** grupo, **quiero** ejecutar la imagen en VPS y documentar lo observado, **para** entregar un proyecto accesible y verificable.

**Criterios de aceptación**:

- [ ] Imagen desde python:3.12-alpine, dependencias en capa previa, usuario sin privilegios y HEALTHCHECK ready.
- [ ] docker run con variables externas, restart unless-stopped y puerto documentado; sin Compose.
- [ ] Seed se ejecuta dentro del contenedor; datos sobreviven al recrearlo.
- [ ] D-01 a D-07 con comandos/salidas reales; validación pública desde fuera de VPS.
- [ ] DEPLOY con URL, fecha/hora reales, build/run completos sin secretos y procedimiento de actualización.
- [ ] README con integrantes y pasos locales desde cero; ZIP conforme al formato de entrega.
- [ ] Servicio en línea hasta notas; convivencia con proyecto existente revisada antes de publicación.

**Reglas relacionadas**: RT-CFG-01 y 02. Ejercicios 7 y 8; contexto del usuario para convivencia.

## Fuente

Consigna: páginas 7–16. Historias de usuario: organización documental de esos requisitos, no nuevos pedidos funcionales.
