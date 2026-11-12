# Tasks

## 1. Preparación y referencia

- [x] 1.1 Comprobar que el entorno en la nueva ubicación permite usar Python/dependencias y PostgreSQL privado sin leer `.env` real ni tocar la VPS; ejecutar suite previa de C-02 antes de editar existentes, registrar resultado real en `docs/evidencia/TDD-C03.md` y detener ante fallas preexistentes.
- [x] 1.2 Preparar fixtures HTTPX + lifespan y datos aislados reutilizando infraestructura existente; verificar al menos dos casos de aislamiento y limpieza limitada a recursos propios en PostgreSQL privado.

## 2. Editoriales y convenciones compartidas

- [x] 2.1 Bajo RED ejecutado → GREEN → triangulación, crear DTO de editorial y POST `/editoriales/`, verificando 201, extra/id rechazado 422, duplicado 409 propio/rollback y nombres distintos; registrar evidencia por ciclo y explicar DTO/201/409 en README.
- [x] 2.2 Bajo TDD agregar GET lista/detalle y PATCH editorial: verificar paginación, orden, ID inexistente 404, ID no entero 422 sin handler, omisión vs `null`, conflicto 409 y preservación de campos; documentar PATCH en README.
- [x] 2.3 Bajo TDD implementar GET `/editoriales/{id}/libros`: padre inexistente 404, existente sin libros 200 vacío y varios libros paginados con precarga; comprobar límites y ausencia de carga perezosa.

## 3. Géneros y autores

- [x] 3.1 Bajo TDD crear DTO/servicio/router de géneros: POST/GET lista y libros por género; verificar 201, duplicado 409, extra 422, paginación, género inexistente 404 y existente vacío 200. Documentar rutas y ejemplos sin semillas inventadas.
- [x] 3.2 Bajo TDD crear DTO/servicio/router de autores: POST, GET/PATCH por ID; verificar 201, actualización parcial, `null` y extra 422, IDs no entero/inexistente, nombres repetidos permitidos y datos sin restricciones adicionales; documentar rutas.
- [x] 3.3 Bajo TDD GET `/autores/{id}/libros`: verificar 404, lista vacía, varios libros paginados y rol/orden propios del autor, incluidos autores con igual orden; precargar relaciones y probar que no hay SQL por fila.

## 4. Alta de libro con autorías

- [x] 4.1 Bajo TDD crear DTO de entrada anidada: probar un autor y varios, lista vacía 422, campos extra en libro y autoría 422, roles y orden válidos/inválidos; documentar mínimo uno como interpretación confirmada del diagrama.
- [x] 4.2 Bajo TDD validar precio Decimal positivo con máximo dos decimales y precisión NUMERIC(10,2), stock no negativo: probar `0.01`, cero, negativo, `1.23`, `1.234`, límite y exceso, sin guardar importes redondeados; explicar precisión en README.
- [x] 4.3 Bajo TDD POST `/libros/` persiste libro y autorías en una sola transacción: verificar 201 y detalle de uno y varios autores, género presente/ausente, sin SELECT previo de unicidad o existencia de FK mediante inspección de SQL; registrar evidencia RED antes del código.
- [x] 4.4 Bajo TDD verificar ISBN duplicado, editorial/género/autor inexistentes y autor repetido con 409 propio, rollback total observado desde otra sesión y recuperación posterior; no exponer SQL ni nombres internos. Cubrir casos C-02 y C-04 del PDF.

## 5. Lectura, búsqueda y PATCH de libro

- [x] 5.1 Bajo TDD GET `/libros/`: incluir editorial/género, orden estable, paginación default/límites y filtros combinados título/género; probar coincidencias case-insensitive, sin resultados, `%` y `_` literales, cadena C-08 y parámetros inválidos 422; comprobar SQL ligado.
- [x] 5.2 Bajo TDD GET `/libros/{id}`: verificar 404/422, detalle con y sin género, múltiples autorías con rol/orden y desempate estable; medir igual número de consultas con uno y varios autores, sin SQL de lazy loading.
- [x] 5.3 Bajo TDD PATCH `/libros/{id}`: verificar cambio de un campo preservando omitidos y autorías, `genero_id: null` desvincula, `null` en obligatorios y `autores`/extra producen 422; además probar precio inválido, ISBN duplicado y FK inexistente con rollback y 409 propio.
- [x] 5.4 Documentar en README ejemplos de alta, lectura, filtros y PATCH, distinción null/omisión, limitación de autorías y respuesta de error; contrastar ejemplos con rutas realmente verificadas.

## 6. Integración y evidencia

- [x] 6.1 Registrar y comprobar las 16 operaciones y sus métodos en la aplicación junto con rutas de salud; verificar aplicación async, OpenAPI y regresión de startup/sesiones sin conexiones al importar.
- [x] 6.2 Ejecutar suite completa de pytest con PostgreSQL privado, validación estricta OpenSpec y comprobaciones de dependencias; documentar resultados reales, escenarios y tabla `Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR` en evidencia. Confirmar limpieza de recursos propios y marcar sólo tareas realmente verificadas, informando cualquier desviación sin inventar ciclos.
