# C-08 — evidencia parcial en VPS (12 de noviembre de 2026)

Registro de salidas comunicadas por Franco durante el despliegue manual. URL definitiva: `https://parcial2-api.maurodip.me`; también se usó la URL temporal `https://totones-parcial2-api.fqtdaq.easypanel.host`. No se incluyen credenciales.

## Topología observada

- VPS con EasyPanel; el plan limita a tres proyectos. La API nueva `parcial2-api` y PostgreSQL `parcial2-db` se agregaron al proyecto existente `totones` como servicios separados de la calculadora.
- PostgreSQL no se expuso públicamente. Host interno `totones_parcial2-db`, puerto `5432`. La API fue construida desde GitHub con el Dockerfile del repositorio y `SQL_ECHO=false`.
- Uvicorn informó `0.0.0.0:8000` y dos `GET /health/ready` internos con 200.
- El usuario ejecutó `python -m app.demo_seed` en el servicio API. Resultado: editorial 1, género 1, autores 1 y 2, libros 1 a 4, cliente 1.

## Publicación y diagnóstico

- El subdominio temporal resolvió por DNS a la VPS. El dominio de EasyPanel inicialmente apuntaba al puerto 80 del contenedor y se corrigió a 8000.
- Franco agregó `parcial2-api.maurodip.me` a EasyPanel y confirmó que `https://parcial2-api.maurodip.me/health/ready` mostró `{"estado":"listo"}` por HTTPS. No se creó un registro individual en Namecheap durante esta sesión; un registro comodín es una explicación posible, aún no inspeccionada.
- Nginx del host ocupaba el puerto 80 y sólo servía `/var/www/html` con `server_name _`; `easypanel-traefik` estaba 0/1 y fallaba con `failed to bind host port 0.0.0.0:80/tcp: address already in use`.
- Tras autorización del usuario, éste detuvo nginx con `sudo systemctl stop nginx`. Traefik pasó a 1/1 y escuchó en 80 y 443. Posteriormente el usuario ejecutó `sudo systemctl disable nginx`; `systemctl is-enabled nginx` devolvió `disabled` y `easypanel-traefik` seguía 1/1. Nginx sólo servía la página predeterminada; no se observó recuperación de los dominios de la calculadora.
- Traefik devolvía 502 para varios dominios. Desde Traefik, `wget` al nombre VIP `totones_parcial2-api:8000` falló con `Host is unreachable`; a `tasks.totones_parcial2-api:8000/health/ready` respondió HTTP 200 y `{"estado":"listo"}`. Ambos servicios comparten la red overlay `easypanel`.
- Forzar la actualización de Traefik no resolvió el 502. Con revisión explícita, el usuario ejecutó `docker service update --endpoint-mode dnsrr totones_parcial2-api`; después informó que `/health/ready` funcionó públicamente. Este ajuste puede ser sobrescrito por un nuevo despliegue de EasyPanel y debe revalidarse.
- El dominio existente de la calculadora devolvía 502 después de levantar Traefik. **No se comprobó su recuperación**; no afirmar continuidad del producto anterior.

## Pruebas funcionales comunicadas

- `/libros/` en el dominio temporal mostró los cuatro libros del seed.
- El usuario ejecutó POST `/ventas/` con cliente 1 y dos renglones: libro 1 × 2 y libro 4 × 1. La respuesta compartida incluyó venta ID 2, fecha `2026-11-12T21:02:55.438224Z`, precio unitario 25000.00 y subtotal 50000.00 para Rayuela, precio 27000.00 y subtotal 27000.00 para Respiración artificial, total `77000.00`. No se compartió el encabezado con el código HTTP de esa petición.
- Para D-04, el usuario ejecutó `docker service update --force totones_parcial2-api` y confirmó que la API volvió a estar lista. Luego consultó `GET /ventas/2`: la venta persistía con total `77000.00` tras recrear la tarea del servicio. No se confirmó en este paso el estado de la calculadora.
- Para D-06, el usuario ejecutó `docker exec <contenedor de la API> id -u` en la VPS y obtuvo `100`: el proceso se ejecuta sin UID root.
- Para D-05, el usuario ejecutó `docker run --rm --network none <imagen de la API>` sin `DATABASE_URL` y sin publicar puertos. El arranque falló con `ConfigurationError` (`DATABASE_URL debe indicar una base PostgreSQL con controlador asyncpg`) y código de salida `3`; `--rm` retiró el contenedor descartable. El comando se representa con marcadores para no registrar identificadores de imagen dependientes del entorno.
- Para D-01, el usuario inspeccionó en la VPS `python:3.12-alpine`: tamaño `74.098.022` bytes, menor al límite de 100 MB de la imagen base. No confundirlo con el tamaño de la imagen final de la API.
- Para D-07, la primera búsqueda de `Comprobante emitido para venta 2` no devolvió coincidencias. Se corrigió el registro del aviso en el commit `0792fce` para emitirlo también mediante el logger de Uvicorn. Franco implementó esa versión desde GitHub en EasyPanel, volvió a aplicar `docker service update --endpoint-mode dnsrr totones_parcial2-api` tras el despliegue y confirmó que `/health/ready` funcionó. Luego creó la venta 3 (`2026-11-13T02:17:58.607949Z`) con los libros 1 × 2 y 4 × 1, total `77000.00`; el comando `docker service logs --since 10m totones_parcial2-api 2>&1 | grep -F "Comprobante emitido"` devolvió `INFO: Comprobante emitido para venta 3 por 77000.00`. La respuesta de venta se compartió antes de consultar el log. El código HTTP de POST no fue aportado.

## Pendiente

No presentar lo anterior como cierre de D-01 a D-07. Faltan continuidad de la calculadora, procedimiento de actualización durable y evidencia completa de construcción/estado saludable en VPS. El aviso posterior a la venta ya quedó demostrado. El dominio definitivo, la imagen base menor de 100 MB, persistencia de la venta, proceso sin root y fallo sin URL sí fueron observados en VPS. Las pruebas equivalentes de C-07 constan por separado como **locales**.

