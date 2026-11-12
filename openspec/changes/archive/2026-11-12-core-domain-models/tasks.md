# Tasks

## 1. Red de seguridad y aislamiento

- [x] 1.1 Ejecutar la suite existente de C-01 con el runner del entorno y PostgreSQL privado antes de modificar archivos existentes; registrar baseline real en `docs/evidencia/TDD-C02.md` y detener la tarea ante una falla previa, sin repararla por cuenta propia. Verificación: salida real de pytest, contrastada con las 51 pruebas históricas sin asumir que siguen verdes.
- [x] 1.2 Preparar los auxiliares/fixtures de datos de dominio necesarios reutilizando `tests/conftest.py` y `tests/pg_cluster.py`; demostrar mediante dos casos independientes que no se comparten datos y que la limpieza/rollback sólo afecta recursos privados de prueba. Documentar la estrategia junto a las fixtures y su verificación en la evidencia de C-02.

## 2. Tablas y tipos persistidos

- [x] 2.1 Bajo RED→GREEN→triangulación, declarar las nueve clases de tabla y sus columnas exactas en los seis `models.py` previstos; conservar PK entera generada, PK compuesta sin ID de LibroAutor y nulabilidad sólo de genero_id. Verificar en `tests/integration/test_domain_schema.py` persistencia/lectura de entidades completas, dos entidades con IDs generados, NULL de género aceptado y NULL de cada campo obligatorio rechazado en PostgreSQL; adaptar con prueba RED la expectativa temporal de metadata vacía de `test_database.py` cuando corresponda, manteniendo el orden registro→create_all.
- [x] 2.2 Bajo TDD, concretar Decimal/NUMERIC(10,2)/(12,2) y fecha con zona horaria; verificar en `test_domain_schema.py` roundtrip de `0.10`, mínimos y máximos representables, exceso de precisión rechazado, y fechas UTC/con otro offset que conservan el instante. Inspeccionar tipos reales, precisión y escala en PostgreSQL.
- [x] 2.3 Documentar en README el mapa de nueve clases/tablas, ubicación modular y diferencia entre tabla persistida y objeto Python, tipos y nulabilidad; verificar que los nombres/columnas coinciden con la spec y enlazar pruebas/evidencia sin afirmar resultados todavía no ejecutados.

## 3. Restricciones e índices

- [x] 3.1 Bajo TDD, implementar UNIQUE de editorial.nombre, genero.nombre, libro.isbn, cliente.email y perfil_cliente.cliente_id, y unicidad de la PK de autoría; verificar en `tests/integration/test_domain_constraints.py` valores distintos aceptados, cada duplicado rechazado, parejas distintas aceptadas y mismo orden válido entre autores distintos aceptado. Escribir sin SELECT previo de unicidad.
- [x] 3.2 Bajo TDD, implementar los siete CHECK de precio/stock/orden/rol/total/cantidad/precio_unitario; parametrizar en `test_domain_constraints.py` los cuatro roles válidos, rol inválido, límites válidos, cero y negativos según cada regla. Verificar rechazos por escrituras reales que no dependan de validación Python y triangular cada comportamiento con caso válido y borde inválido.
- [x] 3.3 Bajo TDD, implementar las ocho FK con referencias exactas; verificar en `test_domain_constraints.py` cada referencia existente aceptada, cada identificador inexistente rechazado y genero_id NULL aceptado, sin agregar políticas de borrado/cascadas.
- [x] 3.4 Bajo TDD, agregar los seis índices FK explícitos y verificar por inspector/catálogo en `test_domain_schema.py` cobertura de las ocho FK; probar que la PK compuesta cubre libro_id por prefijo inicial y UNIQUE cubre perfil_cliente.cliente_id, mientras autor_id dispone de índice propio. Verificar también que no se duplican esos dos índices ya cubiertos.
- [x] 3.5 Documentar en README las diferencias PK/FK/UNIQUE/CHECK/índice y la razón de cada FK en la tabla dependiente; incluir la matriz de ocho FK y las dos coberturas reutilizadas. Verificación: concordancia con el esquema inspeccionado y trazabilidad RN-01/02/03/09 y RT-DB-04.

## 4. Relaciones bidireccionales

- [x] 4.1 Bajo TDD, concretar back_populates de editorial/libros, género/libros, libro/autorías y autor/autorías; verificar en `tests/integration/test_domain_relationships.py` navegación de los dos extremos con una y varias autorías, distintos roles/órdenes y género ausente. Precargar explícitamente cada camino recorrido y comprobar que el recorrido posterior no emite SQL.
- [x] 4.2 Bajo TDD, concretar Cliente.perfil escalar opcional y su inversa; verificar en `test_domain_relationships.py` cliente sin perfil, con perfil recuperado como objeto y navegación inversa, con todas las relaciones utilizadas precargadas y sin SQL posterior. Conservar la prueba de segundo perfil rechazado de 3.1.
- [x] 4.3 Bajo TDD, concretar cliente/ventas, venta/renglones y libro/renglones; verificar en `test_domain_relationships.py` ambas direcciones con una y varias ventas/renglones, cantidades y precios propios conservados, precarga de todos los caminos recorridos y cero SQL durante el recorrido posterior.
- [x] 4.4 Documentar en README agregación, asociación y composición con ejemplos del modelo, navegación `libro.autorias[i].autor`, perfil opcional y diferencia entre back_populates y precarga; verificar que no atribuye a C-02 altas HTTP atómicas, cálculos de venta, orden estable ni políticas de borrado todavía no implementadas.

## 5. Recuperación transaccional

- [x] 5.1 Bajo TDD, verificar en `tests/integration/test_domain_transactions.py` transacción conjunta de libro/autorías: un caso válido confirma todas las filas; un caso con autoría inválida produce IntegrityError, rollback y ausencia de todas las filas de esa transacción observada desde otra sesión. Confirmar una escritura válida posterior con la sesión recuperada y registrar evidencia sin introducir service/endpoint de C-03.
- [x] 5.2 Bajo TDD, verificar en `test_domain_transactions.py` transacción conjunta de venta/renglones: un caso válido persiste cabecera/detalle; otro con renglón inválido exige rollback y no deja filas parciales. Confirmar recuperación de la sesión y documentar en la evidencia que esta prueba valida persistencia, mientras precios/total y alta HTTP corresponden a C-05.

## 6. Registro completo y arranque aditivo

- [x] 6.1 Bajo TDD, completar/reutilizar register_models y extender `tests/integration/test_database.py`: arrancar en una base privada vacía crea las nueve tablas sin tabla health; un segundo lifespan conserva datos de dominio; una tabla ajena y sus datos/estructura se conservan; create_all sigue sin alterar columnas existentes. Verificar registro antes de creación y evitar dependencia del orden global de tests o resets de una base real.
- [x] 6.2 Actualizar README con creación de tablas al startup, límite de create_all frente a tablas existentes y ausencia de seed/migraciones/reset, más instrucciones reales de verificación de modelos; comprobar coherencia con el lifespan observado y los casos de 6.1. Completar progresivamente la evidencia TDD de cada grupo sin fabricar salidas.

## 7. Integración del change

- [x] 7.1 Ejecutar la suite completa y validación estricta de OpenSpec; comprobar regresión de health, importación sin red y ciclo de vida de C-01. Completar `docs/evidencia/TDD-C02.md` con resultados reales y tabla `Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR`; resumir decisiones/límites y marcar únicamente tasks verificadas, dejando C-02 listo para revisión sin archivar, publicar ni hacer commit/push.















