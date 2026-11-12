# Recorrido HTTP C-01 a C-08

Ejecutar `python -m app.demo_seed` con la API detenida o en otra terminal. Copiar sus IDs JSON a las variables `@` de `C-01-a-C-08.http`. Son variables del cliente REST, no números fijados por el proyecto. Ejecutar bloques `###` en orden. Los POST adicionales guardan el ID devuelto con `client.global.set`; funciona con la extensión REST Client de VS Code. Cada bloque indica el estado esperado.

Los casos C-01 a C-08 son la matriz de errores/seguridad de la consigna. El mismo archivo recorre además las 26 operaciones distintas, marcadas con `[OP nn]`. Las peticiones que crean datos pueden volver a dar 409 si se repiten: para una segunda demostración completa usar otra base aislada o cambiar las claves de los ejemplos. El seed sí se puede repetir sin duplicar.

Para verificar de una vez el archivo exacto sin instalar REST Client, definir `PG_BIN` como en el README principal y ejecutar `python -m test.verify_examples`. El script crea un PostgreSQL privado, sustituye las variables por los IDs reales del seed, ejecuta las peticiones en orden, comprueba los códigos esperados y elimina ese clúster al terminar.
