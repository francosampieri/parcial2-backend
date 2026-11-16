# Spec Delta

## Purpose

Permitir que las pantallas del primer parcial consulten y modifiquen la API real de la librería, mostrando estados, paginación, importes históricos y errores del servidor.

## ADDED Requirements

### Requirement: Cliente HTTP único y rutas de la API

La aplicación SHALL centralizar la URL base `/api` y las peticiones `fetch`. SHALL conservar la barra final de las rutas que la API la exige, por ejemplo `/api/libros/` y `/api/ventas/`, y SHALL NOT construir SQL ni URLs de backend dentro de las pantallas. Los errores de conexión y las respuestas 409/422 SHALL mostrarse como mensajes legibles, sin trazas internas.

#### Scenario: Petición exitosa
- **WHEN** una pantalla solicita un recurso mediante el cliente HTTP
- **THEN** la petición usa la base `/api`, la ruta y el método esperados, y la respuesta se entrega a la pantalla

#### Scenario: Error del servidor
- **WHEN** la API responde 409 o 422
- **THEN** la pantalla muestra el mensaje devuelto por el servidor o un mensaje propio comprensible, sin romper la interfaz

### Requirement: Catálogo conectado a la API

La pantalla de catálogo SHALL cargar `GET /libros/` con `titulo`, `limit` y `offset`, y SHALL reiniciar el desplazamiento al cambiar la búsqueda. Cada elemento SHALL mostrar título, ISBN, precio, editorial y género; un género nulo SHALL mostrarse como «Sin clasificar». Al abrir el detalle de un libro, la pantalla SHALL consultar `GET /libros/{id}` y mostrar sus autores con rol y orden. SHALL distinguir carga, lista vacía, búsqueda sin coincidencias y error de conexión.

#### Scenario: Búsqueda y paginación
- **WHEN** el usuario busca por una parte del título y cambia de página
- **THEN** la lista se actualiza con los resultados de la API y el desplazamiento vuelve a cero al cambiar el filtro

#### Scenario: Detalle con autores
- **WHEN** el usuario abre el detalle de un libro
- **THEN** se consulta `GET /libros/{id}` y se muestran los autores con su rol y orden

#### Scenario: Estados del catálogo
- **WHEN** la API responde con una lista vacía, una búsqueda sin resultados o un error
- **THEN** la pantalla muestra el mensaje correspondiente sin confundir los tres estados

### Requirement: Altas de libros y clientes contra la API

La pantalla de libros SHALL cargar editoriales y géneros desde `GET /editoriales/` y `GET /generos/`, y SHALL enviar `POST /libros/` con título, ISBN, precio positivo, stock entero desde cero, editorial, género opcional y al menos una autoría con `autor_id`, `rol` y `orden`. Para validar un autor SHALL usar `GET /autores/{id}`. La pantalla de clientes SHALL enviar `POST /clientes/` con nombre y email, y SHALL permitir recuperar un cliente por ID con `GET /clientes/{id}`. Una alta exitosa SHALL usar los datos devueltos por la API; un 409 o 422 SHALL mostrar el mensaje del servidor y conservar los datos del formulario.

#### Scenario: Alta de libro válida
- **WHEN** se completa el formulario con al menos una autoría y referencias existentes
- **THEN** la API responde 201 y el libro aparece en las vistas que se recarguen

#### Scenario: Conflicto o validación
- **WHEN** se repite un ISBN o email, o se envía un campo inválido
- **THEN** la pantalla muestra el mensaje del 409 o 422 y no presenta el alta como exitosa

#### Scenario: Búsqueda de cliente por ID
- **WHEN** el usuario ingresa un ID de cliente existente
- **THEN** la pantalla consulta `GET /clientes/{id}` y muestra su nombre y email

### Requirement: Venta conectada a la API

La pantalla de ventas SHALL enviar `POST /ventas/` con `cliente_id` y renglones que contengan sólo `libro_id` y `cantidad`. SHALL exigir al menos un renglón, cantidades enteras positivas y un solo renglón por libro. Mientras la petición está en curso SHALL deshabilitar el botón de confirmación. Con la respuesta 201 SHALL mostrar los precios unitarios, subtotales y total devueltos por el servidor, limpiar el formulario y permitir consultar el historial. Ante 409 o 422 SHALL conservar el borrador de la venta.

#### Scenario: Confirmación de venta
- **WHEN** se confirma una venta válida con uno o más renglones
- **THEN** la respuesta 201 muestra los importes calculados por la API y el formulario queda limpio

#### Scenario: Rechazo de venta
- **WHEN** el cliente o un libro no existe, o el contrato es inválido
- **THEN** la pantalla muestra el 409 o 422 y mantiene los renglones para corregirlos

### Requirement: Historial y precios históricos

La pantalla de historial SHALL listar `GET /ventas/` con `limit` y `offset`, y SHALL consultar `GET /ventas/{id}` al abrir el detalle. El detalle SHALL mostrar fecha, cliente, renglones, precios unitarios y subtotales, y SHALL conservar los importes originales aunque el precio del libro haya cambiado después.

#### Scenario: Listado y detalle
- **WHEN** el usuario abre el historial y selecciona «Ver detalle»
- **THEN** la lista se pagina con la API y el detalle se obtiene de `GET /ventas/{id}`

#### Scenario: Precio histórico
- **WHEN** se modifica el precio de un libro después de una venta
- **THEN** el detalle de la venta anterior sigue mostrando el precio y subtotal registrados
