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
| G-07 Despliegue | Build local, HTTPS/proxy y persistencia en VPS | Local OK; VPS pendiente |

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

## Pendiente de la VPS

- Publicar el servicio `frontend` en EasyPanel con Build Path `/frontend` y `API_UPSTREAM`.
- Configurar el dominio HTTPS y verificar `/api/health/ready` desde fuera.
- Repetir G-01 a G-07 contra la URL pública y adjuntar capturas/salidas sanitizadas.
- Registrar URL, fecha y hora del despliegue público en `DEPLOY.md`.
- Regenerar el ZIP después de publicar para que la entrega tenga la URL y la evidencia finales.

## Empaquetado

```sh
.venv/bin/python scripts/empaquetar_global.py
```

Resultado observado: `dist/Parcial_Global_totones.zip`, **114 archivos**, **127.9 KiB**, con esta raíz:

```text
Parcial_Global_totones/
  frontend/
  backend/
  README.md
  DEPLOY.md
  evidencia/
```

El script verificó que incluye ambos Dockerfiles, `frontend/default.conf.template` y los `env.example`, y que no contiene `.env`, `.venv`, `__pycache__`, `.git`, `tmp/` ni dependencias instaladas. El ZIP actual es preliminar: se regenera después de la publicación para incorporar la URL y la evidencia pública.

