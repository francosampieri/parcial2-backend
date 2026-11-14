# Proposal

## Why

La API y su imagen ya funcionan en un entorno local, pero el parcial exige una instancia accesible desde fuera, evidencias reales de la VPS y un paquete de entrega. EasyPanel tiene el límite de tres proyectos del plan contratado y los tres están ocupados. La API y una base nueva deben instalarse como servicios distintos dentro del proyecto existente `totones`, sin alterar los servicios, la base ni los dominios de `calculadora`.

## What Changes

- Guiar al usuario para que inspeccione en modo lectura el proyecto `totones` y la conectividad de la VPS, y comparta capturas o salidas sanitizadas; confirmar nombres de servicios libres, URL, PostgreSQL independiente, permisos y plazo del campus sin solicitar acceso SSH al agente.
- Preparar junto al usuario los cambios concretos de infraestructura, comandos y plan de vuelta atrás antes de ejecutarlos en la VPS. Elegir el mecanismo compatible con EasyPanel y con las evidencias de `docker run` pedidas por la consigna a partir de sus observaciones.
- Guiar al usuario para crear en `totones` un servicio nuevo de API y otro de PostgreSQL, sin crear un cuarto proyecto ni modificar `calculadora`; publicar la imagen de C-07 con configuración privada externa, `SQL_ECHO=false`, usuario no root, salud y reinicio persistente, y ejecutar el seed en la base nueva.
- Guiar las comprobaciones externas de salud, catálogo y ventas, y documentar D-01 a D-07 con fecha, comandos y resultados reales sanitizados aportados por el usuario. Comprobar conservación de datos al recrear sólo el servicio de este parcial.
- Completar README y DEPLOY con los valores públicos y el procedimiento de actualización; preparar `Parcial_Cap1a4_totones.zip` sin secretos ni archivos temporales. Un integrante hará la subida al campus.

## Capabilities

### New Capabilities

- `vps-publication-and-delivery`: publicación aislada y verificable de esta API en la VPS del grupo, documentación de evidencias reales y paquete académico reproducible.

### Modified Capabilities

Ninguna. Los contratos de `container-image` y `reproducible-demonstration` siguen vigentes; este change comprueba su uso en la VPS y completa la entrega.

## Impact

- Infraestructura: proyecto EasyPanel `totones` en la VPS existente, dos servicios nuevos y ruta pública propia, operados manualmente por el usuario siguiendo un plan específico; el agente sólo guía e interpreta resultados. `calculadora` queda fuera del alcance.
- Repositorio: DEPLOY.md, README.md, evidencia D-01 a D-07 y ZIP de entrega; no se prevén cambios funcionales en la API.
- Riesgos: interferencia con el producto alojado, secretos en evidencias, conflicto entre el flujo EasyPanel y el comando `docker run` solicitado por la consigna, y resultados de publicación no verificables. La inspección previa resuelve estos puntos antes de ejecutar cambios.
