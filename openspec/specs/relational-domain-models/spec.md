# relational-domain-models Specification

## Purpose

Garantizar que el catálogo, los clientes y las ventas dispongan de un esquema relacional íntegro, con referencias verificables, importes exactos y relaciones navegables para los casos de uso posteriores.

## Requirements

### Requirement: Esquema persistente fiel al dominio

El sistema SHALL persistir exactamente las nueve tablas de negocio siguientes, conservando sus nombres y columnas: `editorial(id,nombre,pais)`, `genero(id,nombre)`, `autor(id,nombre,nacionalidad)`, `libro(id,isbn,titulo,precio,stock,editorial_id,genero_id)`, `libro_autor(libro_id,autor_id,rol,orden)`, `cliente(id,nombre,email)`, `perfil_cliente(id,cliente_id,telefono,direccion)`, `venta(id,cliente_id,fecha,total)` y `renglon_venta(id,venta_id,libro_id,cantidad,precio_unitario)`. Las tablas con `id` SHALL tener PK entera generada; `libro_autor` SHALL usar la PK compuesta `(libro_id,autor_id)` sin columna `id`. Los campos persistidos SHALL ser no nulos salvo `libro.genero_id`. La ausencia de un perfil SHALL representarse sin una fila de perfil, manteniendo obligatorio el cliente de cualquier perfil existente.

#### Scenario: Persistencia de entidades completas
- **WHEN** se guardan entidades con todos sus campos requeridos y referencias válidas
- **THEN** sus datos se recuperan en las tablas y columnas indicadas, con identificadores enteros generados para las tablas con `id`

#### Scenario: Campo obligatorio nulo
- **WHEN** se intenta persistir NULL en una columna de negocio diferente de `libro.genero_id`
- **THEN** la base rechaza la escritura

#### Scenario: Género y perfil opcionales
- **WHEN** se guarda un libro sin género y un cliente sin fila de perfil
- **THEN** ambas entidades se conservan sin exigir una entidad dependiente ficticia

### Requirement: Unicidad garantizada por la base

La base SHALL garantizar unicidad de `editorial.nombre`, `genero.nombre`, `libro.isbn`, `cliente.email` y `perfil_cliente.cliente_id`, además de la PK de cada tabla. Un mismo autor SHALL poder intervenir en varios libros y un libro SHALL admitir varios autores distintos; la pareja libro/autor SHALL ser única. El orden de autoría SHALL NOT adquirir una restricción de unicidad adicional.

#### Scenario: Valores distintos aceptados
- **WHEN** se insertan nombres, ISBN y emails distintos, perfiles para clientes distintos y parejas libro/autor distintas
- **THEN** la base conserva todas las filas válidas

#### Scenario: Valores únicos repetidos
- **WHEN** se repite cualquiera de los nombres únicos, ISBN o email ya persistidos
- **THEN** la base rechaza la segunda fila aunque no exista una comprobación previa de unicidad

#### Scenario: Segundo perfil o autoría duplicada
- **WHEN** se intenta guardar otro perfil del mismo cliente o repetir la misma pareja libro/autor
- **THEN** la base rechaza la escritura duplicada

#### Scenario: Orden compartido por autores distintos
- **WHEN** dos autores distintos de un libro tienen el mismo orden válido
- **THEN** la base acepta las dos autorías sin agregar una regla de unicidad ausente en la consigna

### Requirement: Valores y precisión del dominio

La base SHALL imponer `libro.precio > 0`, `libro.stock >= 0`, `libro_autor.orden >= 1`, `libro_autor.rol IN ('autor','coautor','traductor','ilustrador')`, `venta.total >= 0`, `renglon_venta.cantidad > 0` y `renglon_venta.precio_unitario > 0`. Los precios SHALL persistirse como `NUMERIC(10,2)` y el total como `NUMERIC(12,2)`, recuperándose como decimales exactos. `venta.fecha` SHALL persistir un instante con zona horaria. C-02 SHALL NOT calcular totales, copiar precios ni imponer reglas adicionales de stock; estas operaciones corresponden al caso de uso de ventas posterior.

#### Scenario: Valores límite válidos
- **WHEN** se guardan precio y precio unitario `0.01`, stock y total `0`, cantidad y orden `1`, y cualquiera de los cuatro roles admitidos
- **THEN** la base acepta esos valores

#### Scenario: Valores fuera del dominio
- **WHEN** se intenta guardar precio o precio unitario `0` o negativo, stock o total negativo, cantidad u orden menor que `1`, o un rol fuera de la lista
- **THEN** la base rechaza cada escritura por la restricción correspondiente

#### Scenario: Importes exactos y límites de representación
- **WHEN** se guardan decimales con dos cifras fraccionarias dentro de la precisión declarada, incluyendo `0.10` y el máximo representable de cada campo
- **THEN** se recuperan con su valor decimal exacto y un valor que exceda la precisión es rechazado por PostgreSQL

#### Scenario: Fecha conserva el instante
- **WHEN** se guarda una fecha con zona horaria, incluyendo una con desplazamiento distinto de UTC
- **THEN** su lectura devuelve una fecha consciente de zona que representa el mismo instante, aunque PostgreSQL normalice su desplazamiento

### Requirement: Referencias válidas e indexadas

La base SHALL garantizar las ocho FK `libro.editorial_id→editorial.id`, `libro.genero_id→genero.id`, `libro_autor.libro_id→libro.id`, `libro_autor.autor_id→autor.id`, `perfil_cliente.cliente_id→cliente.id`, `venta.cliente_id→cliente.id`, `renglon_venta.venta_id→venta.id` y `renglon_venta.libro_id→libro.id`. Cada FK SHALL contar con un índice que permita buscar por esa columna, mediante un índice explícito o la cobertura de un índice existente con esa columna como prefijo inicial. El modelo SHALL NOT añadir borrados en cascada como consecuencia de este change.

#### Scenario: Referencias existentes
- **WHEN** las ocho clases de referencia apuntan a filas existentes y el género opcional es válido o NULL
- **THEN** se pueden persistir los objetos relacionados

#### Scenario: Referencia inexistente
- **WHEN** se intenta persistir cualquiera de las ocho FK con un identificador inexistente
- **THEN** PostgreSQL rechaza la escritura

#### Scenario: Índices de referencias
- **WHEN** se inspecciona el esquema creado sobre una base vacía
- **THEN** cada FK queda cubierta por un índice válido para búsquedas por ella, incluyendo `autor_id` de la PK compuesta cuya primera columna es `libro_id`

### Requirement: Navegación bidireccional sin perder datos de asociación

El dominio SHALL permitir navegar en ambos sentidos entre editorial/libros, género/libros, libro/autorías, autor/autorías, cliente/perfil, cliente/ventas, venta/renglones y libro/renglones. La autoría SHALL ser una entidad con rol y orden accesibles al recorrer libro→autoría→autor. El perfil del cliente SHALL ser un objeto opcional y las relaciones a varios SHALL ser colecciones. La navegación de relaciones precargadas SHALL funcionar sin consultas implícitas posteriores.

#### Scenario: Catálogo relacionado
- **WHEN** se recupera con precarga un libro con editorial, género y varias autorías con distintos roles y órdenes
- **THEN** se puede navegar por ambos extremos conservando los datos de cada autoría sin emitir SQL adicional al recorrer lo ya cargado

#### Scenario: Cliente con y sin perfil
- **WHEN** se recuperan con precarga clientes, uno con perfil y otro sin perfil
- **THEN** el primero expone un objeto de perfil que permite volver al cliente y el segundo expone ausencia de perfil, sin listas ni SQL implícito

#### Scenario: Venta con varios renglones
- **WHEN** se recupera con precarga una venta con cliente y varios renglones asociados a libros
- **THEN** las relaciones permiten navegar por ambos extremos y conservan cantidades y precios de cada renglón sin SQL adicional al recorrer lo cargado

### Requirement: Rechazo transaccional recuperable

Las restricciones SHALL rechazar escrituras inválidas dentro de una transacción asincrónica sin persistir una parte de esa transacción. Después del error y un rollback explícito, la sesión SHALL poder utilizarse para otra operación válida. Esta garantía de persistencia SHALL verificarse sin anticipar los servicios HTTP de altas compuestas.

#### Scenario: Autoría inválida revierte el libro pendiente
- **WHEN** una misma transacción intenta guardar un libro nuevo y una autoría inválida, y se revierte tras el error de integridad
- **THEN** no quedan persistidos ni ese libro ni sus autorías y la sesión permite guardar otra entidad válida

#### Scenario: Renglón inválido revierte la venta pendiente
- **WHEN** una misma transacción intenta guardar una venta nueva y un renglón inválido, y se revierte tras el error de integridad
- **THEN** no quedan persistidos ni esa venta ni sus renglones y la sesión puede utilizarse nuevamente
