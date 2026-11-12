# Design

## Context

Ver `proposal.md` para la motivación. C-01 está archivado y dejó seis módulos de negocio con `models.py` vacíos, `register_models()` que ya importa esos módulos y `initialize_database()` que llama a ese registro antes de `SQLModel.metadata.create_all` dentro de `engine.begin()`. El motor y `async_sessionmaker(expire_on_commit=False)` pertenecen al lifespan y viven en `app.state`; no hace falta reconstruir esta infraestructura.

Las pruebas actuales usan pytest/pytest-asyncio y un clúster PostgreSQL 17.10 privado creado por `tests/pg_cluster.py` y expuesto desde `tests/conftest.py`, compatible con el mínimo PostgreSQL 16 de la consigna. La evidencia previa registra 51 pruebas verdes; ese número es contexto histórico y debe reconfirmarse al iniciar apply. `tests/integration/test_database.py` contiene una expectativa temporal de metadata global vacía: debe evolucionar con el nuevo contrato, conservando la comprobación de orden registro→creación.

Fuentes: KB 04/05/06/08/09/10, C-02 de `CHANGES.md`, tabla y navegación del PDF (páginas 4–5), y specs principales `application-foundation`/`health-monitoring`. Las guías locales de PostgreSQL y testing complementan estas fuentes sin añadir políticas Supabase ni otros dominios. El delta de fundación retira explícitamente el requisito temporal «Creación aditiva de tablas registradas» y lo reemplaza por «Creación aditiva de tablas del dominio», manteniendo sus dos escenarios de creación/conservación y retirando el permiso de registro vacío. El CLI admite deltas de requirements, pero impide omitir escenarios de un bloque MODIFIED: REMOVED/ADDED expresa esta sustitución con motivo y transición, sin conservar títulos obsoletos ni editar anticipadamente las specs principales.

## Goals / Non-Goals

**Goals:** establecer un único mapeo de tablas de dominio reutilizable por servicios posteriores, con integridad verificable en PostgreSQL real y relaciones aptas para carga anticipada. Las pruebas distinguen esquema físico, persistencia, navegación y ciclo de vida.

**Non-Goals:** construir contratos o servicios HTTP, imponer mínimos de colecciones mediante triggers, calcular precios/totales, definir DELETE o cascadas, cargar seed o operar sobre la VPS. La composición venta/renglones se representa aquí mediante FK y colección; su alta indivisible por HTTP se implementa en C-05. Los tests transaccionales de C-02 sólo comprueban la base y la sesión existentes.

## Decisions

### 1. Modelos por módulo y registro central existente

Ubicar `Editorial` en editoriales, `Genero` en generos, `Autor` en autores, `Libro` y `LibroAutor` en libros, `Cliente` y `PerfilCliente` en clientes, `Venta` y `RenglonVenta` en ventas. Declarar `__tablename__` explícito en cada tabla y clases `SQLModel, table=True`; health sigue sin tabla.

Usar referencias de relaciones por nombre y, cuando haga falta, imports bajo `TYPE_CHECKING`, evitando imports circulares de ejecución. Completar todo el registro antes de configurar mappers o acceder a relaciones. Reutilizar `register_models()`; cambiar su documentación o imports sólo si es necesario.

**Alternativa:** un archivo global para las nueve clases evita algunos imports, pero incumple la organización modular acordada. Añadir un registro nuevo duplica el punto de inicialización sin aportar comportamiento.

### 2. Tipos y nulabilidad explícitos, sin valores inventados

Las ocho PK simples usan `int | None` en Python para permitir instancias nuevas sin ID y una PK entera generada por PostgreSQL; la columna persistida no es nullable. LibroAutor declara sus dos FK enteras como PK compuesta y no agrega ID propio. Se preservan las columnas exactas de la spec.

Usar `str` sin máximos arbitrarios, `int` para cantidades/stock/orden, `Decimal` con `Numeric(10,2)` o `Numeric(12,2)` explícitos, y `datetime` con `DateTime(timezone=True)`. `genero_id` es `int | None`, FK nullable; las otras columnas persistidas son no nulas. Que un cliente no tenga perfil no vuelve nullable `perfil_cliente.cliente_id`: simplemente no existe esa fila. Sólo el género está marcado como nulo permitido en la tabla fuente. No agregar normalización de email, validación matemática de ISBN ni defaults de precio, rol, orden, stock, total o fecha. C-05 suministrará fecha/total y precios calculados por el servidor.

**Alternativa:** `float` facilita ejemplos pero introduce aproximación binaria; `datetime` sin zona pierde semántica del instante; NULL y defaults generalizados esconderían datos ausentes. `Enum` nativo exigiría un tipo PostgreSQL adicional; `str` más CHECK cumple la lista de roles con menor complejidad. El límite decimal se prueba con valores de dos decimales; la política de entradas con más decimales se define al diseñar DTO, sin añadir ahora una regla de redondeo.

### 3. Integridad declarativa en la base

Declarar UNIQUE de los cinco campos indicados, PK compuesta de autoría y los siete CHECK de la spec, preferiblemente con nombres estables para diagnosticarlos en pruebas. Las ocho FK apuntan a las tablas indicadas. No duplicar garantía con SELECT previo ni agregar restricciones ausentes (orden único por libro, unicidad de nombre de autor, libro único por venta, mínimo de autorías/renglones en la DB). Las dos últimas reglas de colección pertenecen a contratos posteriores según sus fuentes.

**Alternativa:** validar únicamente al construir objetos deja la DB expuesta a escrituras directas inválidas. Los tests deben ejecutar INSERT/flush/commit reales, incluso usando Core cuando corresponda para evitar que una validación Python oculte la ausencia de CHECK/NOT NULL en el esquema.

### 4. Índices sin duplicación innecesaria

Cada FK tiene cobertura de búsqueda por su columna. Agregar índices explícitos de una columna en `libro.editorial_id`, `libro.genero_id`, `libro_autor.autor_id`, `venta.cliente_id`, `renglon_venta.venta_id` y `renglon_venta.libro_id`. La PK `(libro_id,autor_id)` cubre `libro_autor.libro_id` como prefijo inicial; el índice único de `perfil_cliente.cliente_id` cubre esa FK. Verificar cobertura real por catálogo/inspector PostgreSQL y documentar estas dos reutilizaciones.

**Alternativa:** indexar cada FK además de PK/UNIQUE satisface búsquedas pero duplica dos índices, consume espacio y encarece escrituras. Suponer que el segundo componente de una PK compuesta cubre búsquedas por autor no cumple la garantía de prefijo inicial elegida.

### 5. Relaciones con back_populates y objeto de asociación

Usar estos pares: `Editorial.libros↔Libro.editorial`, `Genero.libros↔Libro.genero`, `Libro.autorias↔LibroAutor.libro`, `Autor.autorias↔LibroAutor.autor`, `Cliente.perfil↔PerfilCliente.cliente`, `Cliente.ventas↔Venta.cliente`, `Venta.renglones↔RenglonVenta.venta` y `Libro.renglones_venta↔RenglonVenta.libro`. El lado con FK es el dependiente: por ejemplo, muchos libros comparten una editorial, por eso la FK va en libro. Perfil es escalar opcional y su FK única garantiza como máximo uno por cliente. LibroAutor permite muchos a muchos con datos propios, navegando `libro.autorias[i].autor`.

Mantener las políticas ORM ordinarias de asociación; no agregar `delete-orphan`, `cascade_delete` ni `ON DELETE CASCADE`. Precargar en los tests mediante joinedload para relaciones a uno y selectinload para colecciones, incluyendo caminos anidados. `back_populates` vincula los extremos del mapeo, pero no precarga automáticamente las colecciones inversas: cada prueba debe cargar explícitamente todos los caminos que vaya a recorrer, o probar cada dirección con consultas separadas adecuadas. No fijar un orden global de colecciones en este change; comparar por IDs/conjuntos cuando el contrato no define orden. No introducir carga automática para todas las consultas: cada servicio posterior elegirá su grafo de precarga. La prueba registra SQL después de materializar el resultado y comprueba cero consultas durante el recorrido.

**Alternativa:** `link_model` como acceso muchos a muchos directo es insuficiente porque oculta rol/orden. Añadir cascadas por interpretar “composición” decidiría una política de borrado que no pide el PDF. Las relaciones bidireccionales permiten navegar; no sustituyen las restricciones de base ni hacen segura una lectura lazy en async.

### 6. TDD de persistencia y adaptación de pruebas temporales

Antes de editar archivos existentes, ejecutar la suite de C-01 y registrar baseline; detener la tarea ante fallas previas. Por cada comportamiento, escribir y ejecutar RED por la ausencia del comportamiento esperado, implementar lo mínimo y confirmar GREEN; triangular con dos o más entradas distintas, incluyendo bordes, y refactorizar sólo en verde. Las agrupaciones de tasks describen resultados cohesivos y no autorizan escribir toda la producción antes de probar.

Crear pruebas en `tests/integration/test_domain_schema.py`, `test_domain_constraints.py`, `test_domain_relationships.py` y `test_domain_transactions.py`; extender `test_database.py` para registro/arranque. Reutilizar fixtures existentes; aislar datos por transacción con rollback o por recursos privados del clúster de pruebas, sin limpiar tablas ajenas. Para probar recuperación tras IntegrityError, hacer rollback explícito y comprobar desde otra transacción la ausencia de filas parciales; después efectuar una escritura válida con la sesión recuperada. Los tests que requieren commits deben limpiar sólo sus propias filas o usar un namespace privado, para no depender del orden de ejecución.

Parametrizar cada CHECK, UNIQUE y las ocho FK con casos válidos e inválidos; verificar nulos, precisión/escala, máximo representable, fecha con offset, PK compuesta y todos los pares de navegación. Para los cambios de C-01, reemplazar la expectativa temporal vacía por registro de nueve tablas sin debilitar el orden registro→create_all. Mantener la prueba de create_all que no altera columnas existentes y añadir conservación de datos reales de dominio y tabla ajena entre dos lifespans. No simular aceptación relacional con SQLite ni mocks.

**Alternativa:** sólo inspeccionar metadata comprueba declaraciones pero no que PostgreSQL haga cumplir los contratos. Probar únicamente HTTP no es viable todavía y mezclaría responsabilidades de C-03/04/05. No se exige un porcentaje arbitrario de cobertura.

## Risks / Trade-offs

- [Imports cruzados o anotaciones no resueltas] → Configurar mappers y persistir/navegar los ocho pares con todos los modelos registrados; importación sin red sigue bajo regresión de C-01.
- [create_all no cambia tablas ya creadas] → Probar sobre PostgreSQL privado y documentar que modelos cambiados no migran una base existente. No usar drop/reset para aparentar una migración.
- [Estado compartido entre pruebas del clúster] → Fixtures transaccionales/recursos privados y limpieza limitada a datos propios; ejecutar suite completa al cerrar apply.
- [Perfil escalar sin UNIQUE físico] → Probar por escritura real que un segundo perfil falla, además de comprobar la forma del objeto recuperado.
- [Una restricción parece funcionar por validación Python] → Probar rechazo en PostgreSQL con flush/commit y comprobar el esquema físico.
- [La precisión decimal puede redondear entradas con más de dos decimales] → No atribuir a NUMERIC una validación que no ofrece; definir validación de entrada al proponer contratos de catálogo/ventas.

## Migration Plan

En apply, desarrollar en el checkout local bajo TDD sin arrancar contra direcciones personales. En una base de evaluación vacía, el lifespan existente creará las nueve tablas; en una base compatible conservará sus tablas/filas y creará las faltantes. No existe migración para esquemas incompatibles: detener una eventual intervención y diseñar un cambio seguro antes de tocar datos reales. Un rollback de código no borra tablas ni revierte esquema; conservarlas evita pérdida de información. La publicación de la VPS sigue fuera de C-02.

## Open Questions

No hay dudas bloqueantes para este change. PA-04/PA-05 (PATCH y NULL de entrada), IN-03/PA-10 (mínimo de autorías), PA-06 (seed) y PA-01/PA-02 (VPS) continúan en sus changes correspondientes; no cambian este esquema persistente ni autorizan decisiones de contrato adelantadas.
