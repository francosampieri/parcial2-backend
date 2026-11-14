# Spec Delta

## Purpose

Publicar la API académica en la VPS del grupo sin afectar el producto existente y entregar evidencia real, documentación y un paquete reproducible del parcial.

## ADDED Requirements

### Requirement: Publicación aislada en la VPS autorizada
La publicación SHALL utilizar dos servicios nuevos y distintos, API y PostgreSQL, dentro del proyecto EasyPanel existente `totones`, sin crear un proyecto adicional. La configuración de conexión SHALL permanecer fuera de la imagen y del repositorio; los servicios, la base y los dominios de `calculadora` SHALL conservarse. La instancia SHALL poder actualizarse sin perder los datos confirmados en la base externa.

#### Scenario: Instalación junto al producto existente
- **WHEN** se publican la API y PostgreSQL como servicios distintos dentro de `totones`
- **THEN** la API usa su propia base y ruta pública, no se crea un cuarto proyecto y `calculadora` sigue operativa con sus servicios, base y dominios anteriores

#### Scenario: Actualización de la aplicación
- **WHEN** se reemplaza únicamente la instancia de la API de este parcial manteniendo su base
- **THEN** las tablas y filas previas siguen disponibles y la instancia vuelve a responder como lista

### Requirement: API pública verificable
La instancia publicada SHALL permitir verificar desde una red externa que la preparación de la API responde HTTP 200, que el catálogo contiene los datos iniciales cargados explícitamente y que una venta de ejemplo devuelve HTTP 201 con total y precios de renglón correctos. El servicio SHALL permanecer disponible hasta la publicación de las notas, sujeto al control del grupo sobre su VPS.

#### Scenario: Comprobación fuera de la VPS
- **WHEN** un cliente externo consulta la URL pública después del despliegue y seed
- **THEN** `/health/ready` responde 200, `/libros/` responde 200 con datos y `POST /ventas/` responde 201 con importes correctos

### Requirement: Evidencia real y sanitizada
La entrega SHALL incluir resultados reales, fechados y atribuibles al entorno correspondiente para los casos D-01 a D-07 de la consigna: tamaño de imagen base, construcción e inicio saludable, consulta externa, persistencia tras recreación, fallo sin configuración de base, usuario no root y aviso posterior de comprobante. La evidencia SHALL distinguir verificaciones locales de las realizadas en la VPS y SHALL excluir secretos y cadenas de conexión privadas.

#### Scenario: Revisión de la evidencia
- **WHEN** se revisan los registros de D-01 a D-07
- **THEN** cada caso presenta comando o procedimiento, resultado observado, fecha y entorno sin revelar credenciales

#### Scenario: Caso no comprobado
- **WHEN** una verificación requerida no puede ejecutarse en la VPS
- **THEN** la documentación la identifica como pendiente y no la declara aprobada

### Requirement: Documentación y paquete de entrega
DEPLOY SHALL registrar URL pública, fecha y hora reales, configuración no secreta, pasos de publicación y actualización, y diagnóstico. README SHALL conservar identificación de totones, sus cuatro integrantes, 2PRO1 y pasos locales. El paquete SHALL llamarse `Parcial_Cap1a4_totones.zip`, contener una carpeta con fuente, dependencias, ejemplo de entorno, casos HTTP, Dockerfile, documentación y evidencias, y SHALL excluir credenciales, entorno virtual, cachés y metadatos Git.

#### Scenario: Preparación del ZIP
- **WHEN** un integrante inspecciona el paquete antes de subirlo al campus
- **THEN** encuentra los artefactos exigidos en una carpeta y no encuentra `.env`, `.venv`, `__pycache__` ni `.git`

#### Scenario: Reproducción por el evaluador
- **WHEN** el evaluador lee README y DEPLOY y consulta la URL publicada
- **THEN** puede identificar al grupo, reproducir localmente los casos y verificar la instancia pública con la información no secreta documentada
