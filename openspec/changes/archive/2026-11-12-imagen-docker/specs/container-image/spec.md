# Spec Delta

## Purpose

Permitir construir y ejecutar la API de librería como contenedor reproducible y seguro, conectado a una base PostgreSQL externa y verificable mediante la salud de la aplicación.

## ADDED Requirements

### Requirement: Imagen Alpine reproducible y sin secretos

La imagen de la aplicación SHALL partir de `python:3.12-alpine`, cuya imagen base publicada SHALL medir menos de 100 MB en la verificación. La construcción SHALL instalar las dependencias declaradas en `requirements.txt` sin caché de pip antes de incorporar el código de la aplicación. El contexto y la imagen SHALL excluir `.env`, `.venv`, `.git`, `__pycache__` y credenciales reales; la configuración de PostgreSQL SHALL suministrarse al ejecutar el contenedor y SHALL NOT estar fijada en la imagen. El límite de 100 MB SHALL NOT aplicarse al tamaño de la imagen final.

#### Scenario: Construcción con base y dependencias indicadas
- **WHEN** se construye la imagen con un daemon Docker disponible
- **THEN** utiliza `python:3.12-alpine`, instala las dependencias y se puede medir por separado la base y la imagen resultante

#### Scenario: Archivos locales confidenciales
- **WHEN** el directorio de trabajo contiene `.env`, archivos de entorno virtual o metadatos Git
- **THEN** esos archivos no forman parte del contexto enviado ni de las capas de la imagen

### Requirement: Proceso sin privilegios y servicio accesible

El proceso principal de la aplicación SHALL ejecutarse con un usuario no root y SHALL servir la API en `0.0.0.0:8000` dentro del contenedor. El puerto del host SHALL poder elegirse al ejecutar el contenedor sin reconstruir la imagen.

#### Scenario: Contenedor iniciado correctamente
- **WHEN** PostgreSQL externo está disponible y se publica un puerto del host hacia el 8000 del contenedor
- **THEN** la API acepta solicitudes por ese puerto y el usuario efectivo del proceso no es root

#### Scenario: Puerto externo distinto
- **WHEN** se publica un puerto del host diferente de 8000
- **THEN** el proceso continúa escuchando en el puerto 8000 interno y responde por el puerto externo elegido

### Requirement: Salud Docker ligada a preparación real

La imagen SHALL declarar una comprobación de salud Docker que consulte `http://127.0.0.1:8000/health/ready`. Una respuesta HTTP 200 SHALL permitir el estado `healthy`; un fallo de conexión o respuesta no exitosa SHALL llevar al estado `unhealthy` según los intervalos de Docker. Un startup fallido por ausencia de `DATABASE_URL` o PostgreSQL inaccesible SHALL impedir que la API quede sirviendo solicitudes.

#### Scenario: Base externa disponible
- **WHEN** la API terminó el arranque y PostgreSQL responde a la comprobación de preparación
- **THEN** el contenedor alcanza el estado `healthy`

#### Scenario: Caída posterior de PostgreSQL
- **WHEN** la base deja de responder después de un arranque correcto
- **THEN** la comprobación de preparación falla y Docker termina marcando el contenedor `unhealthy`

#### Scenario: Configuración o base ausente al arrancar
- **WHEN** se ejecuta el contenedor sin `DATABASE_URL` o con una base inaccesible
- **THEN** el startup falla y el contenedor no queda sirviendo la API

### Requirement: Datos externos conservados al recrear el contenedor

El contenedor de la API SHALL usar una base PostgreSQL externa, sin incluir un servidor de base de datos ni almacenar datos de negocio en su sistema de archivos. Con la misma base, reemplazar el contenedor SHALL conservar las tablas y filas existentes. El seed SHALL poder ejecutarse explícitamente dentro del contenedor sin ejecutarse automáticamente en cada arranque.

#### Scenario: Recreación con la misma base aislada
- **WHEN** se elimina sólo el contenedor de la aplicación y se crea otro con la misma dirección de PostgreSQL
- **THEN** las filas previamente confirmadas siguen disponibles y el arranque sólo agrega tablas faltantes

#### Scenario: Seed explícito
- **WHEN** se ejecuta el comando de seed dentro del contenedor ya iniciado
- **THEN** crea sólo los datos iniciales faltantes y no requiere incluir PostgreSQL en la imagen
