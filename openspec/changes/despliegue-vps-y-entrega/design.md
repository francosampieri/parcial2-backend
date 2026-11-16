# Design

## Context

La API ya tiene imagen Docker construida y verificada localmente (C-07), healthcheck y seed manual. La VPS elegida es la actual del grupo. EasyPanel limita el plan a tres proyectos, ya ocupados; el destino acordado es el proyecto existente `totones`, mediante un servicio nuevo de API y otro PostgreSQL. `calculadora` conserva su API, frontend, base y dominios sin cambios. No se conocen todavía dominio propio, red interna ni nombres de servicios disponibles. Cada integrante tiene su propia clave SSH. El usuario ejecutará manualmente todas las operaciones en la VPS y aportará salidas o capturas sanitizadas; el agente no solicitará acceso SSH ni operará EasyPanel. La guía DEPLOY actual contiene parámetros ficticios y el roadmap propone `docker run`, mientras la instalación real usa EasyPanel.

## Goals / Non-Goals

**Goals:**
- Obtener un plano comprobado de servicios y conectividad dentro de `totones` antes de elegir nombres, ruta pública y mecanismo de publicación.
- Desplegar esta API y su PostgreSQL como dos servicios nuevos en `totones`, sin cambios en `calculadora`.
- Producir evidencias D-01 a D-07 observables y una entrega que otro integrante pueda revisar.
- Guiar cada acción de la VPS para que la ejecute el usuario, interpretando su resultado antes de indicar la siguiente.

**Non-Goals:**
- Crear un cuarto proyecto de EasyPanel o migrar, actualizar o reconfigurar `calculadora`.
- Añadir autenticación, frontend, Compose o cambios funcionales en la API.
- Ejecutar pruebas destructivas en la base existente ni automatizar la subida al campus.
- Acceder directamente por SSH, EasyPanel u otra vía a la VPS desde el agente.

## Decisions

1. **Inspección guiada antes de elegir comandos de despliegue.** Proponer al usuario acciones de sólo lectura en el proyecto EasyPanel `totones` y, si él prefiere, comandos SSH de sólo lectura. A partir de las salidas o capturas que él comparta, relevar servicios existentes, redes, rutas, puertos, recursos y DNS. Registrar inventario sin valores secretos. Alternativa descartada: crear un proyecto nuevo, impedido por el límite del plan, o aplicar ejemplos de `DEPLOY.md` con puerto/base supuestos.
2. **Dos servicios propios dentro de `totones`.** Elegir nombres nuevos para API y PostgreSQL, ruta pública exclusiva para la API y almacenamiento persistente para la base. Conectar por hostname interno verificable y variable privada `DATABASE_URL`; `SQL_ECHO=false`. El usuario de la base tendrá permisos necesarios para las nueve tablas. Alternativa descartada: compartir la base de `calculadora`, que mezclaría datos y aumentaría el riesgo de los casos de prueba.
3. **Publicación en `totones` decidida tras inventario y revisión.** Preferencia por un servicio EasyPanel construido desde el Dockerfile o a partir de la imagen, si permite conservar la configuración de la imagen y cumplir la consigna. Resolver con evidencia real cómo demostrar `docker run` sin sustituir el servicio de EasyPanel ni declarar ejecutados comandos que no se usaron; si hace falta, usar un contenedor descartable aislado para esa demostración. El resultado de la inspección deberá fijar los pasos exactos de los dos servicios, la ruta pública y su reversión; el usuario revisa y ejecuta cada operación manualmente.
4. **Verificaciones guiadas sin tocar el servicio ajeno.** El usuario ejecuta seed sólo en la base nueva y comparte IDs no secretos. Para D-04 él recrea únicamente el contenedor/servicio de este parcial y consulta un registro con ID real antes y después, en una ventana aceptada por el grupo. Para D-05 él usa un contenedor descartable sin `DATABASE_URL` ni puerto público, con reinicio desactivado, dejando intacto el servicio publicado. D-07 se comprueba con respuesta de venta y marca temporal de aviso en logs sanitizados. Alternativa descartada: romper deliberadamente la configuración del servicio publicado.
5. **Evidencia y paquete.** Mantener capturas/salidas sanitizadas con fecha, entorno y resultado por caso D; registrar el proceso efectivo elegido, incluso si un paso de EasyPanel reemplaza una orden manual. Escribir `DEPLOY.md` con comandos/valores públicos reales y procedimiento de reconstrucción/reversión. Crear ZIP mediante lista permitida de archivos y verificar su contenido antes de entregar. La subida al campus permanece manual.

## Risks / Trade-offs

- [EasyPanel no expone directamente la misma secuencia `docker run` de la consigna] → inspeccionar capacidades y decidir si el servicio se publica mediante Docker CLI o si hay una evidencia equivalente aceptable; documentar cualquier diferencia, sin atribuir a la VPS una orden no ejecutada.
- [Nombre de servicio, dominio o red ya ocupados dentro de `totones`] → verificar asignaciones antes de reservarlos; usar nombres propios y una ruta nueva sin tocar dominios de `calculadora`.
- [Acceso a PostgreSQL desde un contenedor nuevo] → probar resolución y permisos sobre una base propia antes de publicar la ruta HTTP; no cambiar acceso de la base del otro proyecto.
- [Secretos en comandos, logs o ZIP] → usar variables/archivo privado o controles de EasyPanel, redactar resultados y comprobar el paquete por lista permitida.
- [Recreación produce breve indisponibilidad] → acordar ventana y plan de vuelta a la imagen/configuración anterior; la base externa permanece.

## Migration Plan

1. Entregar al usuario pasos de inspección de lectura; él comparte resultados sanitizados. Seleccionar recursos propios y confirmar fecha de entrega.
2. Presentar plan específico para dos servicios nuevos dentro de `totones`: nombres de API y PostgreSQL, volumen de la base, DNS/puerto, variables necesarias sin valores privados, método de despliegue, pasos de EasyPanel/comandos, efecto esperado y vuelta atrás. El usuario lo revisa antes de ejecutar cambios ALTO en su VPS.
3. Guiar al usuario para crear sólo esos dos servicios, conectar imagen y base, comprobar salud, seed y URL externa. Tras cada paso, interpretar su resultado. Si falla, guiar la detención de sólo los recursos nuevos, preservando la base persistente si ya contiene datos.
4. Guiar D-01 a D-07 en condiciones controladas, documentar las salidas que aporte el usuario y verificar ZIP localmente.

## Open Questions

- ¿Qué acceso a la interfaz de EasyPanel y a comandos SSH tiene el usuario? No necesita compartir host, usuario ni claves con el agente; se determina mediante los resultados de los pasos guiados.
- ¿Qué nombres de servicio, dominio o puerto libre y hostname interno se usarán dentro de `totones`? Se determinan con inventario y revisión antes de escribir.
- ¿Cuál es el plazo del campus y hasta cuándo deben conservar la instancia accesible? Se confirma antes de calendarizar la entrega.

## Resultado observado

- **Servicios:** `parcial2-api` y `parcial2-db` dentro del proyecto existente `totones`; PostgreSQL privado en `totones_parcial2-db:5432`.
- **URL pública:** `https://parcial2-api.maurodip.me`, revalidada el 16/11/2026.
- **Publicación:** EasyPanel construyó desde GitHub; no se usaron `docker build` ni `docker run` para el servicio publicado. D-05 sí usó un contenedor descartable sin red ni configuración.
- **Entrega:** `Parcial_Cap1a4_totones.zip` fue subido al campus el 16/11/2026, según confirmación del usuario; no se conserva en el repositorio.
- **Límites:** no se verificó la continuidad de `calculadora`; D-02 no tiene evidencia explícita de estado `healthy`; no se capturó el código 201 del POST en la VPS; el ajuste `dnsrr` no es un procedimiento de actualización durable.
