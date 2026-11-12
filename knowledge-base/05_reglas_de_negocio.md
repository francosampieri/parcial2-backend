# Reglas de negocio

Los códigos **RN-01 a RN-12 se conservan del PDF** para trazabilidad. Los códigos adicionales `RT-*` organizan requisitos técnicos de la misma fuente, sin cambiar su origen.

## Catálogo

| Código | Regla | Garante y respuesta |
|---|---|---|
| RN-01 | El ISBN de un libro es único | UNIQUE en PostgreSQL; conflicto 409 |
| RN-03 | Precio del libro > 0 y stock >= 0 | DTO y CHECK en DB |
| RN-11 | Filtrar libros por parte del título sin distinguir mayúsculas | Expresión SQL con parámetros ligados |
| RT-CAT-01 | Editorial obligatoria existente y género opcional existente | FK; alta rechazada → 409 |
| RT-CAT-02 | Cada autoría lleva autor existente, rol y orden | FK, PK compuesta, CHECK de rol/orden y DTO |
| RT-CAT-03 | Rol: autor, coautor, traductor o ilustrador; orden >= 1 | CHECK y contrato de entrada |
| RT-CAT-04 | No preconsultar existencia de IDs al dar de alta un libro | Intentar escritura y traducir `IntegrityError`; rollback |
| RT-CAT-05 | Nombre único de editorial y género | UNIQUE; no comprobación previa de unicidad |

## Clientes

| Código | Regla | Garante y respuesta |
|---|---|---|
| RN-02 | Email de cliente único | UNIQUE; 409 |
| RN-09 | Como máximo un perfil por cliente | UNIQUE en `perfil_cliente.cliente_id`; 409 |

## Ventas

| Código | Regla | Garante y respuesta |
|---|---|---|
| RN-04 | La venta se crea con sus renglones anidados; sin alta independiente | DTO anidado y colección `venta.renglones` |
| RN-05 | Al menos un renglón y sin repetir libro | Validación de DTO; 422 |
| RN-06 | Copiar precio del libro al registrar; conservarlo después | Servidor lee precios; entrada sin precio |
| RN-07 | Total = suma de cantidad × precio unitario | Cálculo servidor con Decimal; entrada sin total |
| RN-08 | Las ventas registran un hecho y no se modifican | Sin PATCH de ventas |
| RT-VTA-01 | Cantidad y precio unitario > 0; total >= 0 | DTO aplicable y CHECK en DB |
| RT-VTA-02 | Cliente y libros de la venta deben existir | Referencia inexistente → 409 propio |
| RT-VTA-03 | Fecha con zona horaria calculada por servidor | Entrada sin fecha |
| RT-VTA-04 | Aviso de comprobante posterior a respuesta | `BackgroundTasks`, función async, `await asyncio.sleep(0.5)` y log |

La consulta necesaria para obtener precios al vender es válida; no confundirla con las preconsultas prohibidas para validar unicidad o FKs del alta de libros.

## Excepciones globales y contratos

| Código | Regla | Garante y respuesta |
|---|---|---|
| RN-10 | Todos los listados: limit por defecto 20, de 1 a 100; offset >= 0 | Restricciones Query; 422 |
| RN-12 | No devolver nombres internos de tablas/restricciones, SQL o trazas | Traducción de errores a mensajes propios |
| RT-HTTP-01 | Alta válida 201; recurso inexistente 404; escritura rechazada 409; contrato inválido 422 | Router/service/DTO según caso |
| RT-HTTP-02 | DTO separados de tablas; altas sin id | Schemas Create/Read/Update |
| RT-HTTP-03 | PATCH aplica sólo campos enviados | `model_dump(exclude_unset=True)` o equivalente |
| RT-DB-01 | Garantías de unicidad y referencias en la DB | UNIQUE/FK/CHECK; no SELECT previo por unicidad |
| RT-DB-02 | Precargar toda relación leída; cero dependencia de lazy loading | joinedload a uno, selectinload colecciones |
| RT-DB-03 | Consultas fijas en detalles aunque aumenten autores/renglones | Medir C-07; conservar evidencia |
| RT-DB-04 | Cada FK con índice y navegación bidireccional | Modelos y esquema PostgreSQL |
| RT-ASYNC-01 | Todos los handlers async, sin operaciones bloqueantes | Sin time.sleep/requests/DB síncrona |
| RT-CFG-01 | DATABASE_URL requerida, sin dirección por defecto | Falta de URL o DB inaccesible impide arranque |
| RT-CFG-02 | Ningún secreto en fuente, repositorio, imagen o ZIP | `.env` excluido; `env.example` sin valores reales |

## Reglas que no se deben inferir como obligatorias

No se especifica descuento de stock al vender, validación de disponibilidad, reservas ni bloqueos de inventario. No se exige unicidad del orden entre autores, validación matemática del ISBN, email normalizado o una política de borrado. Si se decide algo adicional, registrarlo en 09 y cubrirlo con pruebas.

## Fuente

Consigna: páginas 4–8 y 13–15.
