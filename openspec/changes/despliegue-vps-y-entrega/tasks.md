# Tasks

## 1. Inventario y plan revisable

- [ ] 1.1 Guiar al usuario en una inspección de sólo lectura del proyecto `totones` en EasyPanel y de la VPS: servicios actuales, Docker, rutas, puertos, redes y recursos; guardar un inventario basado en sus capturas/salidas sanitizadas y verificar que ningún paso modificó `calculadora` ni otros servicios.
- [ ] 1.2 Confirmar nombres de dos servicios nuevos en `totones` (API y PostgreSQL), volumen persistente, URL/puerto y red propios, permisos, método de publicación compatible con EasyPanel y requisito `docker run`, plazo de campus y permanencia hasta notas; verificar que no se crea un cuarto proyecto ni se comparten base o dominios con `calculadora`.
- [ ] 1.3 Presentar al usuario comandos/pasos exactos, variables sin valores secretos, efecto sobre la VPS y reversión; verificar que su decisión queda registrada antes de indicarle que cree o modifique recursos.

## 2. Publicación controlada

- [ ] 2.1 Guiar al usuario para crear sólo los servicios nuevos de API y PostgreSQL en `totones`, con almacenamiento persistente de la base, y publicar la imagen de C-07 con `DATABASE_URL` privada, `SQL_ECHO=false`, reinicio persistente y ruta propia; verificar con sus resultados salud `healthy`/ready 200 y continuidad de `calculadora`, registrando fecha y procedimiento real en DEPLOY.md.
- [ ] 2.2 Indicar al usuario cómo ejecutar el seed manualmente dentro del servicio API nuevo y conservar sus IDs reales; verificar con sus salidas `/libros/` con datos y que la base de `calculadora` no recibió tablas ni filas del parcial, documentando el comando utilizado.
- [ ] 2.3 Guiar al usuario para comprobar desde una red externa ready 200, libros 200 y venta de dos renglones 201 con precios y total correctos; registrar URL pública, fecha, respuestas sanitizadas y aviso posterior en logs aportados para D-03/D-07.

## 3. Evidencia D y continuidad

- [ ] 3.1 Guiar D-01/D-02/D-06 y registrar comandos y salidas reales aportados por el usuario: imagen base menor a 100 MB, construcción/arranque/estado saludable y proceso no root; verificar que la evidencia identifica entorno y fecha sin secretos.
- [ ] 3.2 En la ventana revisada, guiar al usuario para recrear sólo la instancia de esta API con la misma base y comprobar ready 200 y los IDs/datos previos (D-04); registrar sus resultados y verificar que el producto anterior sigue operativo.
- [x] 3.3 Guiar al usuario en D-05 con un contenedor descartable sin `DATABASE_URL`, sin puerto público y sin reinicio automático; verificar por su salida que falla y no sirve solicitudes, indicar la eliminación de sólo ese recurso y registrar evidencia sanitizada.
- [ ] 3.4 Completar DEPLOY.md y evidencia D-01 a D-07 con URL, fecha/hora, pasos de publicación, diagnóstico y actualización/reversión efectivamente usados; verificar contra los siete casos y señalar explícitamente cualquier caso no comprobado.

## 4. Entrega

- [x] 4.1 Actualizar README con referencia a la URL y entrega, manteniendo pasos locales e integrantes; verificar nombres de Franco Sampieri, Mauro Di Pietro, Tomas Martinez, Renzo Victoria, grupo totones y 2PRO1.
- [x] 4.2 Generar `Parcial_Cap1a4_totones.zip` con una sola carpeta y lista permitida de fuente, dependencias, env.example, test/, Dockerfile/.dockerignore, README, DEPLOY y evidencias; inspeccionar el contenido y verificar ausencia de `.env`, `.venv`, `__pycache__`, `.git` y credenciales.
- [x] 4.3 Guiar una comprobación externa final o usar la URL pública indicada por el usuario y registrar estado/fecha de cierre; verificar accesibilidad y distinguir entrega preparada de subida al campus, que hará un integrante.

