# Decisiones y supuestos

## Mandatos de la consigna

Estas entradas registran decisiones ya tomadas por la cátedra, no elecciones técnicas nuevas del agente.

### DD-01 — API modular asincrónica

**Decisión**: FastAPI con handlers async, SQLModel, SQLAlchemy async, asyncpg y PostgreSQL; organización router/schemas/models/service por módulo.

**Contexto**: ejercicios 1–6 y estructura obligatoria.
**Alternativas consideradas**: arquitectura con repositorios/UoW, DB síncrona o frontend no corresponden al alcance.
**Justificación**: el parcial evalúa esta estructura y sus responsabilidades.
**Trade-offs aceptados**: lógica en services con sesión explícita; no introducir capas adicionales.

### DD-02 — Integridad en PostgreSQL

**Decisión**: UNIQUE, FK, CHECK e índices en modelos/esquema; errores traducidos a mensajes propios.

**Contexto**: RN-01/02/03/09/12 y ejercicio 4.
**Alternativas consideradas**: preconsultar unicidad o cada referencia del alta de libro.
**Justificación**: la DB debe garantizar integridad; el alta de libro no debe hacer SELECT previo de existencia.
**Trade-offs aceptados**: manejar IntegrityError y rollback sin filtrar información interna.

### DD-03 — Esquema por create_all

**Decisión**: importar modelos y crear tablas faltantes al iniciar, sin migraciones para este parcial.

**Contexto**: ejercicio 1.
**Alternativas consideradas**: esquema manual o migraciones quedan fuera de esta entrega.
**Justificación**: requisito explícito de arranque sobre base vacía.
**Trade-offs aceptados**: create_all no altera tablas existentes. Cambios posteriores de esquema exigen una estrategia segura; no borrar datos para simular una migración.

### DD-04 — Venta con composición y precios históricos

**Decisión**: renglones anidados, precios copiados del libro y total/fecha calculados por servidor; sin PATCH ventas.

**Contexto**: RN-04 a RN-08.
**Alternativas consideradas**: recibir precios del cliente, referenciar sólo precio actual o crear renglones aparte.
**Justificación**: preservar el hecho registrado y distinguir asociación de composición.
**Trade-offs aceptados**: importes Decimal y persistencia de valores históricos aun si cambia el catálogo.

### DD-05 — Docker con PostgreSQL externo

**Decisión**: python:3.12-alpine, usuario sin privilegios, HEALTHCHECK ready y docker run sin Compose.

**Contexto**: ejercicios 7 y 8.
**Alternativas consideradas**: slim como base o empaquetar otra base en Compose no cumplen la entrega indicada.
**Justificación**: el VPS ya tiene PostgreSQL y la base Alpine debe estar por debajo de 100 MB.
**Trade-offs aceptados**: verificar dependencias sobre musl y resolver red/variables fuera de la imagen. La imagen final puede superar 100 MB.

### DD-06 — Precarga explícita

**Decisión**: joinedload para relaciones a uno y selectinload para colecciones, sin depender de lazy loading.

**Contexto**: ejercicio 5 y C-07.
**Alternativas consideradas**: cargar relaciones dentro de un bucle o al serializar.
**Justificación**: mantener un número fijo de consultas al aumentar autores/renglones.
**Trade-offs aceptados**: cada consulta debe diseñarse según el DTO de salida; puede haber más de una consulta, pero no una por elemento.

## Decisiones del usuario y del flujo

### DD-07 — Aprendizaje por changes

**Decisión**: changes del tamaño habitual según su cohesión técnica, sin fragmentación artificial; incluir explicaciones didácticas al proponer, preguntar, decidir, resumir e implementar, no sólo al presentar código.

**Contexto**: Franco conoce programación y muy poco FastAPI; integra totones junto con Mauro Di Pietro, Tomas Martinez y Renzo Victoria, de 2PRO1. El usuario aclaró que el acompañamiento debe estar presente durante toda la conversación de trabajo y que no solicita changes pequeños.
**Alternativas consideradas**: fragmentar el trabajo por motivos pedagógicos o limitar las explicaciones al código no refleja la preferencia aclarada.
**Justificación**: el grupo necesita comprender el trabajo además de entregarlo.
**Trade-offs aceptados**: explicar propósito, conceptos, consecuencias y verificación; mantener los checkpoints del flujo, sin convertir las decisiones rutinarias en barreras innecesarias ni reducir artificialmente el alcance de los changes.

### DD-08 — OpenSpec, TDD y fundación sin Discovery

**Decisión**: OpenSpec registra estado de changes; Strict TDD se aplica en implementación con runner disponible; KB por ingesta sin Discovery de mercado.

**Contexto**: instrucciones del usuario y respuesta explícita al checkpoint.
**Alternativas consideradas**: repetir investigación de problema/mercado cuando el PDF ya define el alcance.
**Justificación**: documentar requisitos existentes antes de organizar implementación.
**Trade-offs aceptados**: estas herramientas son del proceso de trabajo y no reemplazan .http ni evidencias de la entrega.

### DD-09 — Convenciones Python y entradas explícitas

**Decisión**: usar snake_case en funciones/variables y anotaciones de tipos en funciones y contratos Python, preservando nombres obligatorios del modelo. Configurar `extra='forbid'` en DTO de entrada, incluidos Create, Update y entradas anidadas; los campos no declarados se rechazan con validación 422.

**Contexto**: reglas 1 y 2 propuestas durante la fase de instrucciones del proyecto el 11 de noviembre de 2026. El usuario aprobó la regla 1 junto con la atomicidad de PR-01 y después aprobó la regla 2 con «me parece bien, incorporala».
**Alternativas consideradas**: convenciones implícitas de nombres/tipos y aceptación silenciosa de campos extra. Se explicó el caso de cliente con nombre/email y un campo edad no declarado que se rechaza con 422.
**Justificación**: hacer explícitos los contratos de entrada y facilitar comprensión y mantenimiento del código. Son decisiones del usuario; no se presentan como requisitos textuales del PDF.
**Trade-offs aceptados**: los consumidores deben enviar sólo campos declarados. La política se limita a DTO de entrada; no impone extra='forbid' a tablas o DTO de salida. Campos obligatorios/opcionales, NULL y semántica de PATCH se resuelven separadamente en cada change.

## Propuestas y su estado

PR-01 fue confirmada por el usuario. PR-02 a PR-04 conservan las decisiones pendientes indicadas; este registro no las convierte en aprobadas.

### PR-01 — Transacciones de altas compuestas

**Decisión confirmada**: confirmar cada libro con todas sus autorías y cada venta con todos sus renglones en una única transacción de la sesión. Si falla una parte, hacer rollback de toda el alta sin persistir datos parciales.

**Motivo**: evitar persistencia parcial ante una FK o CHECK rechazados.
**Alternativas**: commits por entidad simplifican pasos aislados pero pueden dejar datos incompletos.
**Estado**: aprobada por el usuario como regla 3 durante la fase de instrucciones del proyecto el 11 de noviembre de 2026. Se conserva el ID PR-01 para la trazabilidad de su origen como propuesta; falta implementarla y verificarla con pruebas, no decidir su aceptación. No implica introducir Unit of Work.

### PR-02 — Seed reproducible y seguro

**Propuesta**: comando explícito, datos conocidos y repetición sin borrados indiscriminados; usar DB de pruebas aislada para reset.

**Motivo**: demostrar casos locales/VPS y proteger datos del otro proyecto.
**Alternativas**: reset global o seed automático en startup tienen impacto innecesario.
**Estado**: decidir IDs y política de repetición antes de implementarlo.

### PR-03 — Diagnóstico y readiness

**Propuesta**: variable SQL_ECHO para activar SQL localmente; devolver 503 con mensaje propio en ready si DB cae luego de un arranque exitoso.

**Motivo**: evidencia C-07 y estado de salud útil sin filtrar errores.
**Alternativas**: log SQL permanente aumenta ruido; una respuesta 200 durante caída falsearía disponibilidad.
**Estado**: nombres y contrato de error pendientes de concretar; el PDF sólo fija SELECT 1 y 200 cuando está disponible.

### PR-04 — Orden estable y autorías

**Propuesta**: listados con orden estable por ID y autorías por orden; al crear libro, reflejar el mínimo de una autoría del diagrama.

**Motivo**: paginación reproducible y coherencia con figura 1.
**Alternativas**: orden implícito de la DB no es una garantía.
**Estado**: definir en diseño/contratos; la semántica de PATCH de autorías permanece abierta.

## Supuestos inferidos

### SU-01 — Escala académica de grupo

**Supuesto**: scale=team para el desarrollo/evaluación; API públicamente accesible para corrección, sin objetivo de capacidad productiva especificado.
**Origen**: entrega grupal y VPS; cuatro integrantes del grupo totones confirmados por el usuario. La cantidad de integrantes no determina la concurrencia de la API.
**Riesgo si es falso**: pruebas de rendimiento insuficientes para una operación real.
**Cómo validar**: confirmar si se requiere algún volumen/concurrencia concreto; registrado como inferencia de baja confianza en documento 10.

### SU-02 — VPS del usuario y entorno autorizado

**Supuesto**: todavía no se puede afirmar que sean la misma VPS/base que provee la cátedra.
**Origen**: PDF página 11 versus contexto del usuario.
**Riesgo si es falso**: publicar en un entorno que no corresponda a la evaluación o interferir otro proyecto.
**Cómo validar**: confirmar destino/base/puerto permitidos antes de diseñar el despliegue real.

### SU-03 — Sin regla nueva de inventario

**Supuesto**: se conserva stock como atributo validado; no se descuenta ni se rechaza una venta por disponibilidad sin decisión adicional.
**Origen**: ausencia de esa regla en RN-01 a RN-12.
**Riesgo si es falso**: expectativa externa de la cátedra no recogida en PDF.
**Cómo validar**: consultar si existe aclaración adicional de cátedra; no inventar comportamiento obligatorio.

## Fuente

PDF para DD-01 a DD-06; contexto/mensajes del usuario para DD-07 a DD-09 y aprobación de PR-01. Las PR conservan su origen y estado explícito; las SU siguen siendo supuestos, para no mezclarlas con requisitos originales.
