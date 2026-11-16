# Tasks

## 1. Estructura y cliente HTTP

- [x] 1.1 Copiar los HTML y el CSS del primer parcial a `frontend/public/` y verificar que las rutas relativas de navegación, CSS y recursos sigan resolviendo.
- [x] 1.2 Crear `frontend/public/js/api.js` con base `/api`, `fetch` centralizado, barras finales, `limit`/`offset`, parseo de `detail` y normalización de libros, clientes y ventas; verificar con una petición real de catálogo contra el backend local.
- [x] 1.3 Crear `frontend/public/js/formato.js` con formato de importes y fechas, y actualizar las páginas para cargar `api.js` y `formato.js` en lugar de `data.js`.

## 2. Catálogo

- [x] 2.1 Bajo prueba en navegador, conectar `GET /libros/` con búsqueda por título y `limit`/`offset`; verificar lista, búsqueda, reinicio de offset y paginación.
- [x] 2.2 Mostrar título, ISBN, precio, editorial y género, usando «Sin clasificar» cuando el género es nulo; verificar los cuatro libros del seed local.
- [x] 2.3 Implementar el detalle con `GET /libros/{id}` y autores con rol/orden; verificar un libro con uno y con varios autores.
- [x] 2.4 Agregar y verificar estados de carga, catálogo vacío, búsqueda sin coincidencias y error de conexión.

## 3. Altas de libros y clientes

- [x] 3.1 Bajo prueba en navegador, cargar editoriales y géneros desde `GET /editoriales/` y `GET /generos/`, y verificar que los selectores usan datos de la API.
- [x] 3.2 Implementar el alta de libro con título, ISBN, precio, stock, editorial, género opcional y autorías (`autor_id`, `rol`, `orden`), validando el autor con `GET /autores/{id}`; verificar 201 y 409/422.
- [x] 3.3 Implementar el alta de cliente con `POST /clientes/` y la recuperación por ID con `GET /clientes/{id}`; verificar 201, email duplicado 409 y campos inválidos 422.
- [x] 3.4 Verificar que un alta exitosa usa la respuesta de la API y que un rechazo conserva los datos del formulario.

## 4. Ventas

- [x] 4.1 Bajo prueba en navegador, cargar los libros desde la API y permitir agregar, cambiar cantidad y quitar renglones, rechazando duplicados y cantidades inválidas.
- [x] 4.2 Resolver el cliente por ID contra `GET /clientes/{id}` y mostrar su nombre antes de confirmar.
- [x] 4.3 Enviar `POST /ventas/` sólo con `cliente_id` y `libro_id`/`cantidad`; deshabilitar el botón durante el envío y verificar 201.
- [x] 4.4 Mostrar precios unitarios, subtotales y total de la respuesta, limpiar el formulario y conservar el borrador ante 409/422.

## 5. Historial

- [x] 5.1 Conectar `GET /ventas/` con paginación y verificar una venta por página, lista vacía y error.
- [x] 5.2 Implementar «Ver detalle» con `GET /ventas/{id}` y mostrar fecha, cliente, renglones, precios y subtotales.
- [x] 5.3 Verificar que el detalle conserva los importes después de cambiar el precio del libro por PATCH.

## 6. Contenedor y prueba local

- [x] 6.1 Crear `frontend/Dockerfile`, `.dockerignore` y `default.conf.template` y verificar que Nginx sirve `public/` y reenvía `/api/health/ready`.
- [x] 6.2 Ejecutar backend local con PostgreSQL aislado, seed y frontend en Docker; verificar catálogo, alta, venta e historial desde `127.0.0.1:8080`.
- [x] 6.3 Verificar que no se requiere CORS y que la API no recibe peticiones desde un origen cruzado.

## 7. Documentación y cierre

- [x] 7.1 Actualizar README y `frontend/README.md` con estructura, ejecución local y variables; documentar que autores/clientes se buscan por ID.
- [x] 7.2 Actualizar DEPLOY.md con el servicio frontend, Build Path, `API_UPSTREAM`, dominio, proxy y diagnóstico 502, dejando la ejecución en VPS como paso manual posterior.
- [x] 7.3 Ejecutar la suite completa del backend, validar OpenSpec y registrar en `docs/evidencia/G-global.md` la evidencia local; dejar la evidencia pública como pendiente de la publicación manual.
- [x] 7.4 Crear `scripts/empaquetar_global.py` y verificar que `dist/Parcial_Global_totones.zip` contenga `frontend/`, `backend/`, `README.md`, `DEPLOY.md` y `evidencia/`, con ambos Dockerfiles y los `env.example`, sin `.env`, `.venv`, `__pycache__`, `.git` ni dependencias instaladas.
- [x] 7.5 Ejecutar G-02 a G-06 contra la URL pública con datos ficticios y registrar IDs, estados e importes en `docs/evidencia/G-global.md`; verificar libro 201/409, cliente 201/409, venta 201, precio histórico y rechazos 409/422.
- [x] 7.6 Completar G-07: redesplegar el frontend o la API desde EasyPanel y verificar que los datos de la venta 4 y el libro 5 sigan disponibles; luego regenerar el ZIP final.

## Nota de verificación local (16/11/2026)

- Backend: `276 passed` con PostgreSQL privado; sin regresiones.
- OpenSpec: change válido y 8/8 specs válidas.
- Docker: imagen del frontend construida; `/`, `/api/health/ready` y `/api/libros/` respondieron 200 a través de Nginx.
- Navegador: catálogo, altas, venta, historial, 409/422 y precio histórico verificados.
- Empaquetado: `dist/Parcial_Global_totones.zip`, 114 archivos; estructura y exclusiones verificadas con el script.
- Publicación: `https://parcial2.maurodip.me` responde 200; el proxy `/api/` responde 200.
- Pruebas públicas: G-01 a G-07 completadas. Libro ID 5, cliente ID 2, venta ID 4 con total 29000.00; tras el redespliegue del frontend se mantuvieron el libro, la venta, la salud y el catálogo.
- Regenerar el ZIP final y hacer commit/push de la evidencia.


