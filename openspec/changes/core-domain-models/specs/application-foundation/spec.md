# Spec Delta

## REMOVED Requirements

### Requirement: Creación aditiva de tablas registradas

**Reason**: El contrato temporal de C-01 permitía terminar el arranque con un registro de dominio vacío. C-02 lo reemplaza por un contrato que exige las nueve tablas, conservando la creación aditiva y la protección de datos existentes.

**Migration**: Usar el requisito «Creación aditiva de tablas del dominio» añadido en este delta. Mantener el registro previo a create_all y las garantías de conservación; adaptar la expectativa temporal de metadata vacía a registro completo. Esta sustitución de especificación no autoriza borrar ni migrar tablas existentes.

## ADDED Requirements

### Requirement: Creación aditiva de tablas del dominio

El arranque SHALL registrar las nueve tablas del dominio antes de crear las tablas faltantes. La creación SHALL conservar tablas y datos existentes y SHALL NOT alterar estructuras ya creadas. El registro SHALL incluir editorial, genero, autor, libro, libro_autor, cliente, perfil_cliente, venta y renglon_venta, sin inventar tablas de salud.

#### Scenario: Tabla registrada ausente
- **WHEN** el arranque dispone de un modelo registrado y su tabla aún no existe en la base aislada
- **THEN** crea esa tabla antes de atender peticiones

#### Scenario: Tabla y datos ya existentes
- **WHEN** se repite el arranque sobre una tabla registrada que contiene datos
- **THEN** conserva los registros y la estructura existente sin borrados ni recreación

#### Scenario: Registro de dominio completo
- **WHEN** arranca la aplicación sobre una base aislada vacía
- **THEN** las nueve tablas de negocio están creadas antes de atender peticiones, con todas sus referencias resueltas y sin tabla de salud

#### Scenario: Tablas ajenas existentes
- **WHEN** arranca la aplicación sobre una base aislada que también contiene una tabla ajena con datos
- **THEN** crea las tablas de dominio faltantes y conserva la tabla ajena, sus filas y su estructura
