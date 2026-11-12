# Design

## Context

La API FastAPI ya expone 26 operaciones sobre PostgreSQL, y C-05 cerró el flujo de ventas. El proyecto posee pruebas de contrato y aislamiento; C-06 necesita una demostración repetible de la consigna sin alterar esos contratos. Véanse `proposal.md` y `specs/reproducible-demonstration/spec.md`.

## Goals / Non-Goals

**Goals:** un seed seguro para bases existentes, un recorrido de todas las operaciones, evidencia integral real y una guía que pueda seguir otro integrante.

**Non-Goals:** modificar endpoints, agregar migraciones o dependencias de aplicación, resetear una base compartida, desplegar en la VPS (C-08).

## Decisions

### Seed manual y conservador

El seed será un comando Python separado del arranque HTTP. Usará la configuración y sesión de base del proyecto, abrirá una transacción y cerrará sus recursos. Buscará cada entidad por una clave natural estable: nombre de editorial/género, ISBN de libro, email de cliente; para autores, nombre completo más nacionalidad, y para autorías, par libro-autor. Creará sólo los registros ausentes. Si encuentra una clave con atributos diferentes, conservará el registro, mostrará la discrepancia y evitará usar silenciosamente esos datos para una demostración inválida. No hará `DELETE`, `TRUNCATE` ni actualización de filas existentes. Se ejecutará únicamente sobre una base ya inicializada.

Alternativas consideradas: cargar SQL fijo con IDs elegidos obliga a borrar datos o genera colisiones; un seed automático al iniciar produce escrituras inesperadas. Ninguna cumple la política aprobada.

### IDs dinámicos en los casos HTTP

`test/*.http` seguirá la organización C-01 a C-08 de la consigna. Una breve preparación recopilará los IDs que informa el seed y los que devuelven los POST; las variables de los ejemplos referirán esos valores. Comentarios breves marcarán método, ruta y respuesta esperada. El recorrido de 26 operaciones reutilizará esos ejemplos y las pruebas existentes; habrá pruebas nuevas sólo para el comando seed y para huecos de integración reales.

Alternativa considerada: IDs 1, 2 y 4 embebidos reproducen la captura del PDF sólo en una base vacía; dejan de ser fiables tras ejecuciones previas. En un entorno de evaluación aislado se conservarán los importes de la consigna (por ejemplo, dos libros de 25.000 y 27.000, con total 77.000), sin prometer sus IDs.

### Evidencia medida sobre PostgreSQL aislado

La prueba integral verificará creación de catálogo/cliente/perfil, venta de dos renglones, total exacto y precio histórico tras PATCH del libro. La persistencia se observará deteniendo y levantando una nueva instancia contra la misma base. Para C-07 se instrumentarán consultas SQL efectivas durante el GET de detalle de libros con diferente número de autores y ventas con diferente número de renglones, registrando conteo y contexto reproducible en `docs/evidencia/`. La evidencia publicable excluirá contraseñas, URLs con credenciales y datos personales reales.

Alternativas consideradas: inferir el conteo a partir del código o copiar logs de SQL_ECHO no demuestra el resultado de la ejecución; repetir todos los casos CRUD como tests nuevos añade tiempo sin cubrir riesgo adicional.

### README como entrada única

El README enlazará el seed, las variables usadas por `test/*.http`, los comandos de pruebas y la evidencia, junto con grupo, integrantes y curso. Se actualizarán las secciones existentes para no duplicar instrucciones contradictorias.

## Risks / Trade-offs

- [Una clave natural de autor no está protegida por una restricción única] → Si aparecen coincidencias ambiguas, fallar con mensaje claro y pedir intervención manual; jamás elegir una arbitrariamente.
- [Datos existentes con la misma clave pero distinto contenido] → Conservarlos y señalar la discrepancia; la demostración exacta se corre en una base aislada.
- [Cambios futuros en el formato REST Client] → Mantener variables simples y una secuencia explícita de captura de IDs en el README.
- [Medición SQL afectada por preparación del test] → Contar sólo el GET bajo examen, con el seed y la preparación fuera de la ventana medida.

## Migration Plan

No hay cambio de esquema ni migración. Aplicar C-06 agrega archivos y un comando optativo. Para revertirlo, retirar el comando y la documentación; las filas que el seed haya insertado se conservan deliberadamente y cualquier limpieza en una base de prueba requiere una decisión separada.
