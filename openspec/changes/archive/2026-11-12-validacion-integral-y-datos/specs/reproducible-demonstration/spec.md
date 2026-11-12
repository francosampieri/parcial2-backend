# Spec Delta

## Purpose

Permitir que cualquier integrante prepare una base de ejemplo sin perder datos existentes y reproduzca los casos del parcial con evidencia verificable.

## ADDED Requirements

### Requirement: Seed explícito y repetible
El proyecto SHALL ofrecer un comando de seed que cree los datos de ejemplo faltantes mediante claves naturales estables. El comando MUST conservar registros existentes, no borrarlos ni sobrescribirlos, y no ejecutarse automáticamente al iniciar la API.

#### Scenario: Primera carga en una base vacía
- **WHEN** se ejecuta el comando de seed sobre una base inicializada y vacía
- **THEN** se crean las editoriales, géneros, autores, libros con sus autorías y clientes necesarios para los ejemplos, y se informan sus identificadores reales

#### Scenario: Ejecución repetida
- **WHEN** se ejecuta nuevamente el comando sobre una base que ya contiene esos datos
- **THEN** no se crean duplicados ni se modifican los registros existentes

#### Scenario: Coincidencia con datos editados
- **WHEN** una clave natural del seed coincide con un registro existente cuyos demás datos difieren
- **THEN** el comando conserva ese registro y comunica la discrepancia sin reemplazar sus valores

### Requirement: Casos HTTP reproducibles
El proyecto SHALL incluir casos ejecutables para C-01 a C-08 de la consigna, con el resultado esperado documentado. Los casos que dependan de claves numéricas MUST usar identificadores efectivamente devueltos por el seed o por respuestas anteriores, sin asumir IDs fijos en una base existente.

#### Scenario: Demostración desde una base aislada
- **WHEN** un integrante sigue las instrucciones de instalación y ejecuta los casos en orden sobre una base aislada
- **THEN** puede observar respuestas esperadas para las 26 operaciones de la API, incluidos los errores requeridos por la consigna

#### Scenario: Base con identificadores diferentes
- **WHEN** los registros de ejemplo ya existen con identificadores distintos de los obtenidos en una base vacía
- **THEN** los casos pueden ejecutarse usando los identificadores reales informados sin recrear ni borrar esos registros

### Requirement: Evidencia integral y de consultas
La entrega SHALL conservar evidencia verificable de una venta de dos renglones con total exacto y precio histórico, de la persistencia tras reiniciar la API y de que el detalle de libro y venta usa una cantidad fija de consultas SQL frente a relaciones de distinta cardinalidad.

#### Scenario: Venta y precio histórico
- **WHEN** se crea una venta con dos renglones y luego cambia el precio de catálogo de uno de los libros
- **THEN** el total y precio unitario guardados en la venta permanecen iguales a los calculados al crearla

#### Scenario: Reinicio de la API
- **WHEN** se reinicia la aplicación después de crear datos de ejemplo y una venta
- **THEN** los recursos siguen disponibles en PostgreSQL sin volver a ejecutar el seed

#### Scenario: Cardinalidad distinta
- **WHEN** se consulta el detalle de libros con uno y varios autores, y ventas con uno y varios renglones
- **THEN** la evidencia registra el mismo número de consultas SQL para cada tipo de detalle, con los datos sensibles sanitizados

### Requirement: Guía de reproducción
El README SHALL indicar los pasos desde una instalación nueva para inicializar la base, cargar el seed, ejecutar las pruebas y recorrer los casos HTTP, e identificar al grupo totones, sus integrantes y el curso 2PRO1.

#### Scenario: Preparación por otro integrante
- **WHEN** un integrante sigue el README en un entorno local nuevo
- **THEN** dispone de los comandos y referencias necesarios para reproducir la demostración sin acceder a una VPS
