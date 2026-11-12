# Spec Delta

## Purpose

Permitir registrar ventas completas con precios históricos y consultarlas por venta o por cliente, notificando el comprobante sin bloquear la respuesta.

## ADDED Requirements

### Requirement: Alta de venta con renglones anidados

La API SHALL exponer `POST /ventas/` para crear una venta en una sola petición. La entrada SHALL contener `cliente_id` y una lista `renglones` con `libro_id` y `cantidad`; SHALL NOT aceptar `precio_unitario`, `subtotal`, `total`, `fecha`, `id` ni campos desconocidos. La respuesta válida SHALL responder 201 con `id`, `fecha`, `total`, un objeto `cliente` con `id`, `nombre` y `email`, y `renglones` con `libro_id`, `titulo`, `cantidad`, `precio_unitario` y `subtotal`, sin repetir el objeto venta dentro del renglón.

#### Scenario: Alta válida de dos renglones
- **WHEN** se envía una venta con un cliente existente y dos renglones de libros existentes con cantidades válidas
- **THEN** responde 201 con la venta creada, el cliente y los renglones con título, precio copiado y subtotal calculado

#### Scenario: Campos calculados en la entrada
- **WHEN** la petición incluye `precio_unitario`, `subtotal`, `total`, `fecha` o `id`
- **THEN** responde 422 y no persiste ninguna fila

#### Scenario: Contrato de renglones inválido
- **WHEN** la lista de renglones está vacía, repite un `libro_id` o contiene una cantidad menor o igual que cero
- **THEN** responde 422 y no persiste ninguna fila

### Requirement: Precios históricos y cálculo en el servidor

El servidor SHALL leer el precio vigente de cada libro, copiarlo al renglón como importe decimal con dos cifras y calcular `subtotal = cantidad × precio_unitario` y `total` como la suma de los subtotales. La fecha SHALL generarse en el servidor con zona horaria. El precio copiado SHALL conservarse aunque el libro cambie de precio después.

#### Scenario: Total y subtotales exactos
- **WHEN** se registran dos ejemplares de un libro de precio 25000.00 y uno de otro de 27000.00
- **THEN** el total responde 77000.00 y los subtotales 50000.00 y 27000.00

#### Scenario: Precio histórico tras editar el libro
- **WHEN** se consulta una venta después de modificar el precio del libro vendido
- **THEN** el renglón conserva el precio y subtotal registrados originalmente

### Requirement: Alta atómica y referencias existentes

La venta y todos sus renglones SHALL confirmarse como una única operación. Si el cliente o alguno de los libros no existe, la API SHALL responder 409 con un mensaje propio y SHALL NOT dejar venta ni renglones parciales. Un fallo de integridad al confirmar SHALL producir rollback y 409, sin exponer SQL, nombres internos ni trazas.

#### Scenario: Cliente inexistente
- **WHEN** se intenta registrar una venta con un `cliente_id` que no existe
- **THEN** responde 409 y no queda ninguna venta ni renglón persistido

#### Scenario: Libro inexistente
- **WHEN** uno de los renglones referencia un libro que no existe
- **THEN** responde 409 y no queda cabecera ni renglón alguno de esa petición

#### Scenario: Recuperación tras conflicto
- **WHEN** una venta es rechazada por una referencia inválida
- **THEN** una venta válida posterior puede registrarse con la misma sesión de trabajo de la aplicación

### Requirement: Consulta paginada y detalle de ventas

La API SHALL exponer `GET /ventas/` y `GET /ventas/{id}`. El listado SHALL paginar con `limit` entre 1 y 100, por defecto 20, y `offset` mayor o igual que 0; SHALL devolver elementos con `id`, `fecha`, `total` y `cliente`, en orden estable. El detalle SHALL devolver la venta con cliente y renglones completos. Un ID inexistente SHALL responder 404 y un ID de ruta no entero o paginación inválida SHALL responder 422.

#### Scenario: Listado paginado
- **WHEN** existen varias ventas y se consulta el listado con límites válidos
- **THEN** responde 200 con la cantidad solicitada, en orden estable y con total y cliente en cada elemento

#### Scenario: Detalle de venta
- **WHEN** se consulta el ID de una venta existente
- **THEN** responde 200 con cliente y todos sus renglones, incluyendo título y subtotal

#### Scenario: Venta inexistente o paginación inválida
- **WHEN** se consulta un ID inexistente o se envían límites fuera de rango
- **THEN** responde 404 o 422 respectivamente

### Requirement: Ventas por cliente

La API SHALL exponer `GET /clientes/{id}/ventas` con la misma paginación del listado general. SHALL devolver sólo las ventas del cliente indicado y SHALL responder 404 si el cliente no existe. Un ID de ruta no entero SHALL responder 422.

#### Scenario: Cliente con y sin ventas
- **WHEN** se consultan las ventas de un cliente con registros y de otro sin ellos
- **THEN** responde 200 con sus ventas paginadas o con una lista vacía, respectivamente

#### Scenario: Cliente inexistente
- **WHEN** se consultan las ventas de un cliente que no existe
- **THEN** responde 404 sin devolver ventas de otros clientes

### Requirement: Consultas acotadas y aviso posterior

Las consultas de lectura SHALL precargar cliente, renglones y libros utilizados, sin consultas implícitas durante la serialización, y SHALL mantener un número fijo de consultas aunque varíe la cantidad de renglones. Todos los handlers SHALL ser asíncronos. Después de confirmar la venta y responder, la API SHALL agendar una tarea asíncrona que espere `asyncio.sleep(0.5)` y registre el comprobante en el log, sin reutilizar la sesión cerrada de la petición ni impedir que se atiendan otras solicitudes.

#### Scenario: Número fijo de consultas
- **WHEN** se consultan dos ventas con distinta cantidad de renglones
- **THEN** ambas lecturas usan la misma cantidad de consultas SQL

#### Scenario: Aviso después de responder
- **WHEN** se registra una venta válida
- **THEN** la respuesta 201 se entrega antes de que la tarea de comprobante termine y el aviso aparece en el log sin bloquear otras peticiones

#### Scenario: Operaciones excluidas
- **WHEN** se inspecciona el contrato publicado
- **THEN** existen sólo las cuatro rutas de ventas de este change, sin PATCH de ventas, alta suelta de renglones, pagos ni descuento de stock
