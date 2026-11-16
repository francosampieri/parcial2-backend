# Design

## Context

El frontend del primer parcial vive hoy en `../ProgIII-FrontEnd-PrimerParcial` y funciona con `localStorage` y datos de ejemplo. La API ya expone catálogo, clientes, ventas y salud; no tiene `GET /autores/` ni `GET /clientes/`, pero sí consultas individuales. La consigna global pide HTML/CSS/JS nativos, base `/api`, Nginx y publicación manual en EasyPanel. Ver `proposal.md` y las specs para el comportamiento observable.

## Goals / Non-Goals

**Goals:** Dejar el frontend integrado y probado localmente, con el contenedor Nginx listo para publicar manualmente, sin modificar la API.

**Non-Goals:** Cambiar contratos del backend, agregar autenticación, CORS, migraciones, un framework JS, listados nuevos de autores/clientes o ejecutar la publicación en la VPS desde este change.

## Decisions

### Estructura `frontend/` dentro del repositorio

Se copian los HTML, CSS y JS a `frontend/public/` y se agregan `Dockerfile`, `.dockerignore` y `default.conf.template` en `frontend/`. EasyPanel podrá usar Build Path `/frontend`; el backend conserva su Build Path `/`. El ZIP de la global se arma con `frontend/` y una copia del backend como `backend/`.

**Alternativas:** Un repositorio nuevo exige mover el backend y duplicar configuración; dos repositorios separados complican el paquete único pedido por la cátedra.

### Cliente HTTP único con normalización

`js/api.js` concentra `fetch`, la base `/api`, las barras finales y el parseo de errores. Normaliza las respuestas de la API a las formas que ya usan las pantallas (`editorialId`, `generoId`, `clienteNombre`, `tituloLibro`, `precioUnitario`) para reducir el cambio visual. Las funciones puras de formato quedan en `js/formato.js`.

**Alternativas:** Reescribir cada pantalla con los nombres exactos de la API multiplica cambios y riesgo. Guardar la URL absoluta en cada JS impide el proxy `/api/`.

### Consultas individuales para autores y clientes

La API no ofrece listados de autores ni clientes. La UI pedirá un ID, consultará `GET /autores/{id}` o `GET /clientes/{id}` y mostrará el nombre antes de usarlo. Para clientes, además, se conserva en memoria la lista de los consultados o creados en la sesión. Esto sigue la alternativa permitida por la consigna y evita ampliar el backend.

**Alternativas:** Agregar `GET /autores/` y `GET /clientes/` mejora la UX pero abre un change de API no pedido y obliga a más pruebas y despliegue.

### Paginación y estados explícitos

Catálogo e historial usan `limit`/`offset`. El botón «Siguiente» se habilita cuando la página devolvió exactamente `limit` elementos; «Anterior» se deshabilita en `offset = 0`. Cada pantalla distingue carga, vacío, sin resultados y error. No se inventa un total de páginas porque la API no lo devuelve.

**Alternativas:** Cargar todo y paginar en el navegador ignora el contrato; agregar un `total` al backend excede el alcance.

### La API es la fuente de los importes de venta

La pantalla de ventas puede mostrar un total estimado con los precios del catálogo mientras se arma el borrador, pero al confirmar muestra exclusivamente precios, subtotales y total de la respuesta 201. Si hay 409/422, conserva los renglones. El botón se deshabilita durante la petición.

**Alternativas:** Recalcular el total en el navegador después de confirmar duplicaría la regla del servidor y podría mostrar importes distintos.

### Historial con detalle bajo demanda

El listado usa `GET /ventas/` y no trae renglones. «Ver detalle» consulta `GET /ventas/{id}` y renderiza los importes históricos. Así se evita N+1 en el listado y se conserva la composición venta/renglones.

**Alternativas:** Incluir renglones en el listado obliga a tocar la API y multiplica filas.

### Nginx y prueba local antes de la VPS

El contenedor usa `nginx:1.30-alpine`, sirve `public/` y reenvía `/api/` a `${API_UPSTREAM}/`. La prueba local usa un backend con base PostgreSQL aislada y un contenedor con `API_UPSTREAM=host.docker.internal:8000`. No se agrega CORS porque el navegador habla con el mismo origen del proxy. La publicación en EasyPanel se ejecuta manualmente después, con el runbook de `DEPLOY.md`.

**Alternativas:** Servir el frontend con `python -m http.server` exigiría CORS y no reproduce el proxy de producción. Publicar sin probar localmente arriesga la instancia que ya está en línea.

## Risks / Trade-offs

- [La API responde `detail` como texto o como lista] → El cliente HTTP contempla ambos formatos y muestra un mensaje neutro si no puede interpretarlos.
- [Los selectores por ID son menos cómodos] → Se valida el ID contra la API y se muestra el nombre antes de aceptarlo; se documenta la decisión.
- [El frontend viejo dependía de `localStorage`] → Se retira del flujo principal; las pruebas manuales antiguas de persistencia local dejan de aplicar y se reemplazan por evidencia contra la API.
- [La lista de libros no trae autores] → El catálogo pide el detalle al abrir un libro; la tabla de altas usa un botón de detalle en lugar de asumir autores.
- [El proxy interno puede devolver 502 en EasyPanel] → Se documenta el diagnóstico con `tasks.` y `dnsrr`; no se cambia código por un problema de red del despliegue.
- [Escribir pruebas contra la API pública contamina la entrega] → La integración se prueba con un backend y una base locales; la VPS se usa sólo para la evidencia final con datos ficticios.

## Migration Plan

No hay cambios de esquema ni del backend. Se incorpora `frontend/`, se prueba localmente con PostgreSQL aislado y se documenta la publicación manual. Revertir el frontend consiste en volver al commit anterior o retirar el servicio frontend; la API y su base no se tocan. La publicación en EasyPanel queda fuera de la ejecución automática de este change.

## Open Questions

- El dominio público del frontend y si se retira el dominio público de la API se confirman al ejecutar la publicación manual. No cambian el código ni las pruebas locales.
