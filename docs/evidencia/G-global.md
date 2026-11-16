# Evidencia — Evaluación Global (frontend integrado)

Registro de la verificación **local** del frontend contra la API y PostgreSQL.
La evidencia de la URL pública queda pendiente de la publicación manual en EasyPanel.

## Entorno

- Fecha: 16/11/2026.
- Backend: `.venv` con Python 3.14.7, Uvicorn en `0.0.0.0:8001`.
- Base: PostgreSQL 18.6 en un clúster privado temporal, base `libreria_global`, con `python -m app.demo_seed`.
- Frontend: imagen `libreria-frontend-local` sobre `nginx:1.30-alpine`, publicada en `127.0.0.1:8080`.
- Navegador: navegador integrado de OpenCode (Chromium), sin errores de consola en catálogo y libros.
- No se usaron credenciales reales ni la base de la VPS.

## Proxy Nginx

```text
GET /                         → 200
GET /api/health/ready         → 200 {"estado":"listo"}
GET /api/libros/              → 200
```

La API recibió las peticiones a través de `/api/`, sin CORS.

## Casos G

| Caso | Verificación local | Resultado |
|---|---|---|
| G-01 Catálogo | Carga de libros desde `GET /api/libros/`, búsqueda por título, paginación `limit`/`offset`, sin resultados y detalle de autores | OK |
| G-02 Alta de libro | Libro con stock, género opcional y dos autorías; ISBN repetido | 201 y 409 |
| G-03 Alta de cliente | Cliente creado y recuperado por ID; email repetido | 201, consulta 200 y 409 |
| G-04 Venta | Dos renglones, precios/subtotales/total de la respuesta y formulario limpio | 201 |
| G-05 Precio histórico | PATCH del precio del libro y nueva consulta del detalle | Importes originales conservados |
| G-06 Rechazo | Cliente inexistente 409 y renglones repetidos 422; el borrador de la venta se conserva | OK |
| G-07 Despliegue | Build, HTTPS/proxy y persistencia tras redespliegue | Completado |

## Detalle observado

### Catálogo

- Se mostraron cinco libros del backend local: cuatro del seed y uno creado en la prueba.
- `limit=3` produjo dos páginas: 3 elementos en la página 1 y 2 en la página 2; «Limpiar búsqueda» volvió a la página 1.
- La búsqueda `zzzz-no-existe` mostró «No se encontraron libros para «zzzz-no-existe»».
- El libro creado sin género mostró «Sin clasificar».
- El detalle consultó `GET /libros/{id}` y mostró autores con rol y orden.

### Altas

- Libro `Libro Global Uno`, ISBN `978-GLOBAL-0001`, precio 1000.00, stock 5, autor 1: 201 con ID 5 y aparición en la tabla.
- Repetir el ISBN respondió 409 «Conflicto de datos» y no agregó filas.
- Libro `Libro Global Dos` con autores 1 (autor, orden 1) y 2 (coautor, orden 2): 201 y detalle con ambas autorías.
- Cliente `Cliente Global`, email ficticio: 201 con ID 2 y fila en la tabla de sesión.
- Repetir el email respondió 409.
- La búsqueda por ID del cliente 1 mostró «Cliente encontrado: Cliente de ejemplo.».

### Ventas

- Cliente 1 y libros 1 × 2 y 4 × 1.
- La API devolvió venta 1, total `77000.00`, precios `25000.00`/`27000.00` y subtotales `50000.00`/`27000.00`.
- El formulario se limpió después del 201 y la confirmación mostró los importes de la API.
- `POST /api/ventas/` con cliente inexistente respondió 409 `{"detail":"Cliente o libro inexistente"}`.
- `POST /api/ventas/` con el mismo libro dos veces respondió 422 con el mensaje de validación.
- En la UI, el intento con cliente inexistente conservó el renglón cargado.

### Historial

- Se crearon cinco ventas adicionales por API para probar paginación: 6 ventas en total.
- Página 1: 5 filas y «Siguiente» habilitado; página 2: 1 fila y «Siguiente» deshabilitado.
- «Ver detalle» consultó `GET /api/ventas/{id}` y mostró fecha, cliente, renglones e importes.
- Se cambió el precio del libro 1 a `30000.00` con `PATCH /api/libros/1`; después de recargar, el detalle de la venta 1 siguió mostrando `25000.00` y total `77000.00`.

## Verificación pública (16/11/2026)

La aplicación quedó publicada en `https://parcial2.maurodip.me` mediante el servicio
`parcial2-frontend` de EasyPanel, con proxy `/api/` hacia `totones_parcial2-api:8000`.

| Comprobación | Resultado observado |
|---|---|
| `GET /` | 200 con el HTML de El Tintero |
| `GET /api/health/ready` | 200 `{"estado":"listo"}` |
| `GET /api/libros/` | 200 con los libros del seed |
| Catálogo público, página 1 | 3 tarjetas |
| Catálogo público, página 2 | 1 tarjeta; paginación operativa |
| Búsqueda `Rayuela` y detalle | Coincidencia y autor Julio Cortázar con rol/orden |
| Consola del navegador | Sin errores |

G-01 queda cubierto en la URL pública.

## Pruebas públicas G-02 a G-06 (16/11/2026)

Datos ficticios usados: sufijo `20261116-d04254ef`, ISBN
`978-GLOBAL-20261116-d04254ef` y email
`global-20261116-d04254ef@example.test`.

| Caso | Operación | Resultado observado |
|---|---|---|
| G-02 | `POST /api/libros/` con editorial 1, género 1 y autor 1 | 201, libro ID 5, precio 1000.00, stock 2 |
| G-02 | `GET /api/libros/5` | 200 con Julio Cortázar como autor |
| G-02 | Repetir el mismo ISBN | 409 `{"detail":"Conflicto de datos"}` |
| G-03 | `POST /api/clientes/` | 201, cliente ID 2 |
| G-03 | `GET /api/clientes/2` | 200 con el email registrado |
| G-03 | Repetir el mismo email | 409 `{"detail":"Conflicto de datos"}` |
| G-04 | `POST /api/ventas/` con cliente 2, libro 5 × 2 y libro 4 × 1 | 201, venta ID 4, total 29000.00 |
| G-04 | `GET /api/ventas/4` | 200 con los dos renglones |
| G-05 | `PATCH /api/libros/5` a 1500.00 y consultar venta 4 | El renglón conserva 1000.00, subtotal 2000.00 y total 29000.00 |
| G-05 | Restaurar el precio del libro 5 a 1000.00 | 200; la venta 4 no cambia |
| G-06 | Venta con cliente 999999999 | 409 `{"detail":"Cliente o libro inexistente"}` |
| G-06 | Venta con el libro 5 repetido | 422 con el mensaje de renglones repetidos |
| G-06 | Conteo de ventas antes/después | 3 → 4 con la venta válida; los rechazos no agregaron filas |

La venta 4 quedó visible en el historial público:

```text
Venta 4 — 16/11/2026 — Cliente Global 20261116-d04254ef — $29.000,00
Libro Global 20261116-d04254ef: 2 × $1.000,00 = $2.000,00
Respiración artificial: 1 × $27.000,00 = $27.000,00
Total: $29.000,00
```

También se comprobó desde el navegador público que el libro nuevo aparece en el
catálogo y que la venta 4 se abre desde el historial después de recargar.

G-07 quedó completo después del redespliegue manual del frontend: `https://parcial2.maurodip.me/`
siguió respondiendo 200, `/api/health/ready` devolvió 200 `{"estado":"listo"}` y
la venta 4 y el libro 5 siguieron disponibles en la API y en el historial público.
También se verificó el catálogo después del redespliegue, sin errores de consola.

## Pendiente

- Regenerar el ZIP final y hacer commit/push de la evidencia actualizada.




## Empaquetado

```sh
.venv/bin/python scripts/empaquetar_global.py
```

Resultado observado: `dist/Parcial_Global_totones.zip`, **114 archivos**, **aproximadamente 129 KiB**, con esta raíz:

```text
Parcial_Global_totones/
  frontend/
  backend/
  README.md
  DEPLOY.md
  evidencia/
```

El script verificó que incluye ambos Dockerfiles, `frontend/default.conf.template` y los `env.example`, y que no contiene `.env`, `.venv`, `__pycache__`, `.git`, `tmp/` ni dependencias instaladas. El ZIP incluye la URL pública y la evidencia final de G-01 a G-07.

