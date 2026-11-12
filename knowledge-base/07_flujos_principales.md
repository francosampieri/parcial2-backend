# Flujos principales

## Flujo 1: Arranque y apagado

**Disparador**: iniciar uvicorn. **Actor**: desarrollador o Docker.

1. Configuración obtiene DATABASE_URL del entorno/.env, sin URL de respaldo.
2. Lifespan crea motor async y fábrica de sesiones con expire_on_commit=False y los guarda en app.state.
3. Se importan todos los modelos y se ejecuta create_all mediante la conexión asincrónica.
4. Con arranque completo se atienden peticiones. GET live no consulta DB; GET ready ejecuta SELECT 1.
5. Depends(get_session) crea/cierra una sesión por petición.
6. Al apagar se dispone el motor.

**Casos de error**: falta de URL o DB inaccesible → arranque fallido; no dejar el contenedor sirviendo. Caída de DB posterior al arranque → ready no debe informar disponibilidad; código/cuerpo concreto pendientes de decisión.

create_all no altera tablas existentes. No prometer que un cambio de modelo actualiza automáticamente el esquema ni borrar tablas compartidas para corregirlo.

## Flujo 2: Alta de libro con agregación y autorías

**Disparador**: POST /libros/. **Actor**: operador.

1. FastAPI valida LibroCreate: datos del libro, IDs y autorías con rol/orden.
2. Router obtiene sesión por Depends y delega al service.
3. Service construye Libro y sus LibroAutor con los IDs recibidos, sin SELECT previo de existencia ni de unicidad.
4. DB impone UNIQUE/FK/CHECK; la escritura del libro y sus autorías se confirma conjuntamente.
5. Service obtiene los datos necesarios para la respuesta con precarga; router responde 201 con detalle.

**Casos de error**: DTO inválido → 422; ISBN duplicado o referencia inexistente → rollback y 409 propio. No devolver texto de IntegrityError ni dejar un libro incompleto al fallar una autoría.

## Flujo 3: Lecturas y PATCH

**Disparador**: consulta o PATCH. **Actor**: consumidor HTTP.

1. FastAPI valida IDs enteros, paginación y contrato.
2. Service consulta con parámetros ligados y precarga declarada de relaciones que integran la salida.
3. Si se pide recurso inexistente, devuelve 404; un listado válido puede estar vacío.
4. En PATCH se aplican sólo campos enviados con exclude_unset, se confirma y se retorna el contrato de salida.
5. Las omisiones conservan valores anteriores; NULL explícito requiere distinguir campos opcionales de obligatorios.

**Casos de error**: ID no entero → 422 antes del handler; unicidad/CHECK/FK al escribir → 409 propio. La política exacta de NULL en PATCH se documentará con los DTO.

Para detalles de libro/venta: joinedload en relaciones a uno y selectinload en colecciones. Obtener el mismo número de consultas con una y varias relaciones; no cargar una vez por elemento.

## Flujo 4: Alta y lectura de perfil

**Disparador**: POST /clientes/{id}/perfil. **Actor**: operador.

1. Validar ruta/cuerpo y resolver que el cliente exista para responder 404 si corresponde.
2. Intentar crear perfil asociado sin preconsultar unicidad.
3. DB garantiza perfil único con UNIQUE; alta válida → 201, perfil repetido → rollback y 409.
4. Detalle de cliente carga perfil anticipadamente y lo devuelve como objeto opcional.

## Flujo 5: Registrar venta y avisar

**Disparador**: POST /ventas/. **Actor**: operador.

1. Validar cliente_id y renglones: mínimo uno, libro no repetido y cantidad > 0.
2. Service obtiene los libros necesarios para copiar sus precios; propuesta: una consulta por conjunto de IDs.
3. Ante libro/cliente inexistente, responder 409 propio y no confirmar escritura parcial.
4. Crear Venta y RenglonVenta; copiar cada precio, calcular total con Decimal y fecha con zona.
5. Confirmar cabecera y renglones juntos. Leer respuesta con cliente y renglones precargados.
6. Agendar aviso con BackgroundTasks; enviar 201.
7. Función async espera asyncio.sleep(0.5) y escribe aviso en log. La API sigue atendiendo otras peticiones.

Secuencia: Operador → API → DB (confirmar venta); API → Operador (201); tarea async → log del comprobante.

**Casos de error**: contrato inválido → 422; referencias rechazadas → 409; error de escritura → rollback. Agendar aviso sólo tras alta confirmada. El aviso no debe reutilizar la sesión de la petición una vez cerrada.

No se agrega descuento o control de disponibilidad de stock sin una decisión adicional explícita.

## Flujo 6: Verificación local

**Disparador**: implementación de un change. **Actor**: grupo.

1. Leer escenario y diseño del change; ejecutar baseline si se modifican archivos con pruebas existentes.
2. Escribir prueba que falle, comprobar RED, implementar mínimo y comprobar GREEN.
3. Triangular con entradas distintas y cubrir casos del escenario; refactorizar con pruebas verdes.
4. Preparar datos conocidos y ejecutar .http exigidos, con comentarios de respuesta esperada.
5. Medir consultas para C-07 con distintas cantidades de autores/renglones y guardar evidencia real.
6. Acompañar propuestas, preguntas, decisiones, resúmenes e implementación con explicaciones didácticas: conceptos introducidos, propósito de cada elección, recorrido de una petición y cómo reproducir la verificación.

Los pasos TDD y pedagógicos son instrucciones del usuario. Los changes conservan el tamaño habitual según la cohesión técnica; no se fragmentan artificialmente para explicar. Los .http y la evidencia son entregables académicos. No declarar un caso aprobado sin ejecutarlo.

## Flujo 7: Publicación y actualización

**Disparador**: API local y Docker verificados. **Actor**: grupo/administrador de VPS.

1. Confirmar VPS/base/puerto permitidos, servicios existentes y red entre contenedor y PostgreSQL.
2. Preparar variables reales fuera del repositorio y de la imagen; diagnóstico SQL desactivado en VPS.
3. Construir imagen desde python:3.12-alpine y correr con docker run, puerto asignado, env-file y restart unless-stopped.
4. Esperar healthy y comprobar logs de arranque; ejecutar seed del proyecto mediante docker exec.
5. Desde fuera del VPS, probar ready, libros y alta de venta. Registrar URL, fecha/hora reales y comandos sin secretos.
6. Ejecutar y guardar D-01 a D-07, cuidando que recreación y pruebas afecten sólo al contenedor de este proyecto.
7. Para actualizar: reconstruir imagen, retirar el contenedor del proyecto y recrearlo con configuración documentada. La DB externa conserva datos.
8. Mantener en línea hasta notas y preparar ZIP conforme a la consigna.

Los comandos de la consigna no autorizan tocar el otro proyecto de la VPS. Las decisiones de infraestructura con impacto en datos requieren revisión según las instrucciones de gobernanza.

## Fuente

Consigna: ejercicios 1–8 y casos C/D. TDD, explicaciones y convivencia VPS: contexto del usuario.
