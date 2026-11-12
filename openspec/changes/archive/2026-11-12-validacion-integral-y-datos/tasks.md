# Tasks

## 1. Seed reproducible

- [x] 1.1 Registrar la línea base de las pruebas afectadas y agregar primero casos focalizados para seed inicial, segunda ejecución sin duplicados y conservación de datos existentes; verificar RED antes del código y GREEN después.
- [x] 1.2 Implementar el comando manual de seed con claves naturales, transacción y salida con IDs reales; verificar en PostgreSQL aislado que crea los ejemplos y que repetirlo no modifica ni duplica filas.
- [x] 1.3 Cubrir la discrepancia y la ambigüedad de autor con pruebas dirigidas; verificar error claro y ausencia de escrituras parciales, y documentar el comando junto con sus límites en README.

## 2. Recorrido HTTP de la consigna

- [x] 2.1 Crear `test/*.http` para C-01 a C-04, con variables de IDs devueltos y comentarios de resultados esperados; verificar manualmente sus operaciones contra la API y una base aislada.
- [x] 2.2 Completar `test/*.http` para C-05 a C-08, incluida la venta de dos renglones y los errores esperados; verificar que el recorrido cubre las 26 operaciones sin asumir IDs fijos.
- [x] 2.3 Actualizar README con preparación desde cero, orden del recorrido, captura de IDs, grupo totones, cuatro integrantes y 2PRO1; verificar que los comandos documentados funcionan en el entorno local.

## 3. Evidencia integral y SQL

- [x] 3.1 Ejecutar una verificación integral focalizada que compruebe total 77.000 en el escenario aislado, precio histórico tras PATCH y persistencia tras reinicio; guardar resultado real y verificable en `docs/evidencia/`.
- [x] 3.2 Medir las consultas SQL sólo durante el detalle de libro y venta con cardinalidades distintas; verificar conteo fijo por tipo y guardar evidencia sanitizada con método de reproducción.
- [x] 3.3 Ejecutar la suite existente una vez como control final y validar los artefactos del change; registrar resultados y cualquier limitación restante sin añadir pruebas redundantes de CRUD.
