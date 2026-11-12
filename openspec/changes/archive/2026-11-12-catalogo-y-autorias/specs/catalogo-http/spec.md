# Spec Delta

## Purpose

Permitir administrar y consultar el catálogo de librería mediante contratos HTTP claros y persistencia íntegra, conservando los datos de cada autoría.

## ADDED Requirements

### Requirement: Operaciones de referencias del catálogo

La API SHALL exponer POST y GET `/editoriales/`, GET y PATCH `/editoriales/{id}`, GET `/editoriales/{id}/libros`, POST y GET `/generos/`, GET `/generos/{id}/libros`, POST `/autores/`, GET y PATCH `/autores/{id}` y GET `/autores/{id}/libros`. Las altas SHALL responder 201 con el recurso creado; detalle y modificación de ID inexistente y listados relacionados de padre inexistente SHALL responder 404. Los libros de un autor SHALL incluir el rol y orden de esa relación.

#### Scenario: Editorial creada y consultada
- **WHEN** se crea una editorial válida y se consulta por su identificador
- **THEN** el alta responde 201 y la lectura 200 con sus datos

#### Scenario: Referencia inexistente
- **WHEN** se consulta o modifica un ID inexistente, o se listan libros de un padre inexistente
- **THEN** la API responde 404

#### Scenario: Libros por autor
- **WHEN** se listan los libros de un autor con varias participaciones
- **THEN** cada resultado conserva el rol y orden correspondientes al autor solicitado

### Requirement: Contratos de entrada y actualización parcial

Las entradas Create y Update SHALL ser distintas de las tablas; Create SHALL NOT aceptar `id` y todas las entradas, incluidas autorías anidadas, SHALL rechazar campos desconocidos con 422. PATCH SHALL actualizar únicamente campos enviados; `genero_id: null` SHALL quitar el género y `null` explícito en otro campo persistente obligatorio SHALL responder 422. PATCH de libro SHALL NOT aceptar `autores`, por lo que las autorías existentes permanecen intactas. Las cadenas no recibirán validaciones adicionales no especificadas.

#### Scenario: Omitir campos en PATCH
- **WHEN** se envía sólo el nuevo título de un libro
- **THEN** cambia el título y los demás valores y autorías permanecen iguales

#### Scenario: Quitar género
- **WHEN** se envía `genero_id: null` en PATCH de un libro con género
- **THEN** el libro queda sin género y conserva los campos omitidos

#### Scenario: Nulos y campos desconocidos
- **WHEN** se envía `null` para un campo obligatorio, `id` en un alta o `autores` en PATCH de libro, o un campo extra en cualquier entrada anidada
- **THEN** se responde 422 sin modificar datos

### Requirement: Alta atómica de libro y autorías

POST `/libros/` SHALL recibir `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id` opcional y `autores` con `autor_id`, `rol` y `orden`; SHALL exigir al menos una autoría. Un libro con todas sus autorías SHALL confirmarse en una sola transacción. El alta SHALL NOT preconsultar unicidad ni existencia de IDs: PostgreSQL garantiza las FK y UNIQUE. Un conflicto de integridad SHALL causar rollback completo y respuesta 409 propia sin SQL, nombres internos ni trazas.

#### Scenario: Alta con varias autorías
- **WHEN** se envía un libro válido con editorial existente y dos autorías válidas
- **THEN** responde 201 con el detalle y quedan persistidos el libro y ambas autorías

#### Scenario: Lista de autorías vacía
- **WHEN** se envía un libro con lista de autores vacía
- **THEN** responde 422 sin persistir el libro

#### Scenario: Referencia o ISBN inválidos
- **WHEN** una editorial, género o autor referenciado no existe, o el ISBN ya existe
- **THEN** responde 409 sin detalles internos y no persiste un libro parcial ni sus autorías

#### Scenario: Autor repetido
- **WHEN** se repite un mismo autor en la lista de un libro
- **THEN** el conflicto de la clave compuesta produce 409 y la transacción completa se revierte

### Requirement: Validaciones y errores del catálogo

El precio de libro SHALL ser Decimal positivo representable en NUMERIC(10,2), con un máximo de dos decimales; el stock SHALL ser entero no negativo, el orden entero mayor o igual a uno y el rol uno de `autor`, `coautor`, `traductor`, `ilustrador`. Contratos o parámetros inválidos SHALL responder 422; un ID de ruta no entero SHALL producir 422 antes de ejecutar el handler. Las escrituras rechazadas por UNIQUE, FK o CHECK SHALL producir rollback y 409 propio, sin filtrar detalles de la base. La cantidad de decimales y los límites de autorías son decisiones confirmadas por el usuario.

#### Scenario: Límites válidos de libro
- **WHEN** se envía precio `0.01`, stock 0 y una autoría con orden 1 y rol permitido
- **THEN** la entrada es válida

#### Scenario: Precio, stock o autoría inválidos
- **WHEN** se envía precio 0, negativo o con más de dos decimales, stock negativo, rol no permitido u orden menor que 1
- **THEN** responde 422 sin escrituras parciales

#### Scenario: Identificador de ruta inválido
- **WHEN** se consulta una ruta con ID no entero
- **THEN** responde 422 sin ejecutar el handler

#### Scenario: Conflicto de unicidad al crear o editar
- **WHEN** se intenta crear o actualizar editorial o género con un nombre repetido, o libro con un ISBN repetido
- **THEN** responde 409 con mensaje propio, sin revelar SQL ni detalles internos

### Requirement: Listados paginados y búsqueda parametrizada

Todos los listados del catálogo SHALL admitir `limit` por defecto 20 entre 1 y 100 y `offset` por defecto 0 y no negativo; parámetros inválidos SHALL producir 422. Los listados SHALL tener orden estable por ID. GET `/libros/` SHALL permitir filtro por parte literal de `titulo` sin distinguir mayúsculas y filtro por `genero_id`, empleando parámetros ligados; SHALL devolver editorial y género. Un padre existente sin libros SHALL devolver lista vacía 200.

#### Scenario: Paginación válida y fuera de rango
- **WHEN** se solicitan páginas sucesivas con limit y offset válidos, o se solicita limit 0 o 101 u offset negativo
- **THEN** las páginas tienen orden estable sin superar el límite y los parámetros inválidos producen 422

#### Scenario: Filtro literal y género
- **WHEN** se filtra por una parte del título con distinta capitalización y por un género
- **THEN** sólo se devuelven libros que cumplen ambos filtros y se incluye su editorial y género

#### Scenario: Texto similar a SQL
- **WHEN** se busca el texto `' OR '1'='1` sobre datos conocidos que no lo contienen
- **THEN** responde 200 con lista vacía y no se altera la consulta con el contenido del texto

#### Scenario: Padre existente sin libros
- **WHEN** se listan libros de un autor, editorial o género existente sin libros
- **THEN** responde 200 con lista vacía

### Requirement: Lectura de libro y carga anticipada

La API SHALL exponer GET y PATCH `/libros/{id}` y GET `/libros/`. El detalle SHALL incluir editorial, género opcional y autores con datos de autoría; sus autorías SHALL ordenarse por `orden` y luego por ID de autor para empates. Las respuestas con relaciones SHALL obtenerlas mediante carga anticipada y SHALL NOT depender de carga perezosa. La cantidad de consultas para detalle de libro SHALL permanecer fija al variar la cantidad de autores.

#### Scenario: Detalle con y sin género
- **WHEN** se consulta un libro con múltiples autores, con género o sin él
- **THEN** responde 200 con editorial, género correspondiente y autorías ordenadas con rol y orden

#### Scenario: Consultas con distinta cantidad de autores
- **WHEN** se consulta el detalle de libros con uno y varios autores bajo las mismas condiciones
- **THEN** ambos se resuelven con el mismo número de consultas y sin consultas por autor
