# Spec Delta

## Purpose

Definir las condiciones de configuración, arranque, persistencia y cierre que permiten ejecutar la API de librería de manera asincrónica y verificable antes de incorporar el dominio.

## ADDED Requirements

### Requirement: Configuración explícita sin secretos de respaldo

La aplicación SHALL obtener `DATABASE_URL` del entorno o del archivo local `.env`, dando prioridad al entorno. La dirección SHALL ser una URL PostgreSQL con controlador asincrónico; un valor ausente, vacío o inválido SHALL impedir el startup sin revelar credenciales. La aplicación SHALL permitir diagnóstico SQL mediante `SQL_ECHO`, desactivado por defecto, con valores booleanos textuales `true` y `false` sin distinguir mayúsculas; otro valor SHALL producir un error de configuración propio. El ejemplo distribuido SHALL contener únicamente marcadores ficticios.

#### Scenario: Entorno tiene prioridad
- **WHEN** existen direcciones distintas y válidas en el entorno y en `.env`
- **THEN** el arranque utiliza la dirección del entorno

#### Scenario: Configuración exclusivamente local
- **WHEN** el entorno no define la dirección y `.env` contiene una dirección válida
- **THEN** el arranque utiliza la dirección local sin necesitar una dirección incorporada al código

#### Scenario: Dirección ausente o inválida
- **WHEN** la dirección está ausente, vacía, mal formada o utiliza un controlador no permitido
- **THEN** el startup falla con un diagnóstico propio que no incluye la dirección completa ni secretos

#### Scenario: Diagnóstico configurable
- **WHEN** se omite `SQL_ECHO` o se configura `false` o `TRUE`
- **THEN** el diagnóstico queda respectivamente desactivado, desactivado o activado

#### Scenario: Booleano inválido
- **WHEN** `SQL_ECHO` contiene un texto diferente de `true` o `false`
- **THEN** el startup falla por configuración inválida sin mostrar secretos

### Requirement: Arranque conectado antes de aceptar peticiones

La aplicación SHALL comprobar una conexión real con PostgreSQL durante su arranque y SHALL atender peticiones sólo después de completar la inicialización. Importar la aplicación SHALL ser posible sin abrir conexiones ni exigir una base accesible. Una conexión rechazada durante startup SHALL abortar el arranque sin dejar un servicio aparentemente listo ni exponer mensajes internos del controlador.

#### Scenario: Arranque con PostgreSQL accesible
- **WHEN** se inicia la aplicación con configuración válida y PostgreSQL disponible
- **THEN** la inicialización termina antes de que se atienda la primera petición

#### Scenario: Arranque con PostgreSQL inaccesible
- **WHEN** la dirección es válida pero la conexión es rechazada
- **THEN** el startup falla y la aplicación no empieza a servir peticiones

#### Scenario: Importación independiente del entorno
- **WHEN** se importa el punto de entrada sin dirección ni servidor configurados
- **THEN** la importación no abre conexiones y la validación pendiente ocurre al iniciar la aplicación

### Requirement: Creación aditiva de tablas registradas

El arranque SHALL registrar los modelos disponibles antes de crear las tablas faltantes. La creación SHALL conservar tablas y datos existentes y SHALL NOT alterar estructuras ya creadas. En C-01 el registro puede estar vacío; las nueve tablas del dominio pertenecen a C-02.

#### Scenario: Tabla registrada ausente
- **WHEN** el arranque dispone de un modelo registrado y su tabla aún no existe en la base aislada
- **THEN** crea esa tabla antes de atender peticiones

#### Scenario: Tabla y datos ya existentes
- **WHEN** se repite el arranque sobre una tabla registrada que contiene datos
- **THEN** conserva los registros y la estructura existente sin borrados ni recreación

#### Scenario: Registro de dominio todavía vacío
- **WHEN** arranca la fundación sin las tablas de C-02
- **THEN** verifica la conexión y completa la inicialización sin inventar entidades de negocio o de salud

### Requirement: Sesiones aisladas por petición

Cada petición que necesite persistencia SHALL recibir su propia sesión asincrónica, reutilizada dentro de esa petición y nunca compartida con peticiones concurrentes. Al terminar la petición, incluso ante una excepción, la aplicación SHALL cerrar la sesión y liberar sus recursos sin confirmar escrituras automáticamente. Los datos ya cargados SHALL seguir disponibles después de una confirmación explícita sin requerir recarga implícita.

#### Scenario: Dos peticiones concurrentes
- **WHEN** dos peticiones usan persistencia al mismo tiempo
- **THEN** reciben sesiones distintas que no comparten transacción

#### Scenario: Dependencia reutilizada dentro de una petición
- **WHEN** dos dependencias de una misma petición solicitan la sesión
- **THEN** reciben la misma sesión durante esa petición

#### Scenario: Cierre normal y con error
- **WHEN** una petición termina normalmente o propaga una excepción con trabajo sin confirmar
- **THEN** su sesión se cierra y ese trabajo no queda persistido

#### Scenario: Lectura posterior a confirmación
- **WHEN** una sesión confirma explícitamente cambios de un objeto cargado
- **THEN** sus atributos cargados siguen disponibles sin una consulta implícita adicional

### Requirement: Liberación de recursos del ciclo de vida

Cada instancia de aplicación SHALL poseer sus recursos de persistencia y SHALL liberarlos al finalizar el ciclo de vida. Si el arranque falla después de crear esos recursos, SHALL liberarlos igualmente. Instancias sucesivas o simultáneas SHALL NOT heredar conexiones ni sesiones de otra instancia.

#### Scenario: Apagado normal
- **WHEN** finaliza el ciclo de vida de una aplicación que inició correctamente
- **THEN** se liberan las conexiones de su motor

#### Scenario: Fallo parcial durante inicialización
- **WHEN** se creó el motor pero falla la conexión o la creación de tablas
- **THEN** se libera el motor antes de propagar el fallo de startup

#### Scenario: Instancias independientes
- **WHEN** se crean dos instancias para ejecuciones distintas
- **THEN** cada instancia utiliza y cierra únicamente sus propios recursos
