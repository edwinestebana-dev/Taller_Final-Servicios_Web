# Pruebas funcionales

Pruebas funcionales documentadas de la API REST, las reglas de negocio, los permisos y la integración interfaz–API–base de datos (Actividad 6 de la guía). Se ejecutan **a mano**, sin herramientas de automatización:

- **Pruebas P-01 a P-11:** desde la documentación interactiva de la API, en `http://127.0.0.1:8000/docs`.
- **Prueba P-12:** desde la interfaz web, en `http://127.0.0.1:8000/`.

Las columnas **Resultado obtenido**, **Estado** y **Evidencia** se completan al ejecutar cada prueba.

## Preparación

1. Partir de una base de datos limpia. Desde la carpeta `backend/`, con el entorno virtual activo:

   ```powershell
   Remove-Item reportes.db -ErrorAction SilentlyContinue
   python -m app.seed
   uvicorn app.main:app --reload
   ```

2. Ejecutar las pruebas **en orden**: cada una parte del estado que deja la anterior, y los ids de los reportes (1, 2, 3) dependen de ese orden.
3. Para enviar una solicitud desde `/docs`:
   - abrir el endpoint y pulsar **Try it out**;
   - escribir el id del usuario en el campo `X-Usuario-Id`;
   - si el endpoint tiene cuerpo, pegarlo en **Request body**;
   - pulsar **Execute** y revisar **Code** y **Response body**.
4. Guardar cada evidencia (captura de `/docs` o de la interfaz) en `evidencias/` con el nombre de la prueba, por ejemplo `evidencias/P-01.png`.

**Usuarios ficticios** (los crea `seed.py`):

| Id | Nombre | Rol |
|---|---|---|
| 1 | Carolina Ruiz | coordinacion |
| 2 | Mateo Gómez | mantenimiento |
| 3 | Laura Pérez | mantenimiento |
| 4 | Andrés Torres | reportante |
| 5 | Sofía Ramírez | reportante |

**Espacios ficticios:**

| Id | Nombre | Tipo | Ubicación |
|---|---|---|---|
| 1 | Aula 101 | aula | Bloque A, piso 1 |
| 2 | Aula 204 | aula | Bloque A, piso 2 |
| 3 | Laboratorio de Química | laboratorio | Bloque B, piso 1 |
| 4 | Sala de Cómputo 3 | laboratorio | Bloque C, piso 3 |
| 5 | Oficina de Coordinación | oficina | Bloque D, piso 2 |
| 6 | Cafetería Central | zona común | Bloque E, piso 1 |

## Resumen

| Id | Prueba mínima (guía) | Requisitos | Estado |
|---|---|---|---|
| [P-01](#p-01) | Registro de un reporte de falla válido | RF-01, RF-02 | |
| [P-02](#p-02) | Registro con datos obligatorios faltantes o inválidos | RF-01, RNF-01 | |
| [P-03](#p-03) | Consulta de reportes y detalle de un reporte | RF-03, RF-04 | |
| [P-04](#p-04) | Consulta de un reporte inexistente | RF-04, RNF-04 | |
| [P-05](#p-05) | Evaluación y actualización válida de un reporte | RF-05 | |
| [P-06](#p-06) | Intento de transición de estado no permitida | RF-05, RF-06 | |
| [P-07](#p-07) | Asignación de un responsable autorizado | RF-06 | |
| [P-08](#p-08) | Intento de gestión por un usuario no autorizado | RF-13, RNF-02 | |
| [P-09](#p-09) | Registro de una intervención válida | RF-07, RF-08 | |
| [P-10](#p-10) | Cierre de un reporte y consulta de su resultado | RF-09, RF-10 | |
| [P-11](#p-11) | Consulta de información consolidada | RF-11, RF-12 | |
| [P-12](#p-12) | Integración interfaz–API–base de datos | RF-14, RNF-07 | |

---

### P-01

| Campo | Valor |
|---|---|
| Identificador | P-01 |
| Prueba | Registro de un reporte de falla válido |
| Requisito relacionado | RF-01, RF-02, RN-01, RN-02 (CA-01) |
| Condiciones iniciales | Base de datos recién cargada con `seed.py`, sin reportes. |
| Pasos | 1. Como Andrés (4), ejecutar `GET /espacios` y comprobar que aparecen los 6 espacios.<br>2. Como Andrés (4), ejecutar `POST /reportes` con el cuerpo indicado.<br>3. Como Andrés (4), ejecutar `GET /reportes/1`. |
| Datos de entrada | `X-Usuario-Id: 4`<br>`{"espacio_id": 3, "tipo_falla": "iluminacion", "descripcion": "La lámpara del fondo no enciende"}` |
| Método y código HTTP esperado | 1. `GET /espacios` → **200**<br>2. `POST /reportes` → **201**<br>3. `GET /reportes/1` → **200** |
| Resultado esperado | El reporte se crea con `id` 1, `estado` `reportado` y `fecha_creacion` automática. El detalle lo muestra asociado al espacio "Laboratorio de Química", ubicación "Bloque B, piso 1". |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-02

| Campo | Valor |
|---|---|
| Identificador | P-02 |
| Prueba | Registro con datos obligatorios faltantes o inválidos |
| Requisito relacionado | RF-01, RNF-01, RNF-04, RN-01 (CA-01) |
| Condiciones iniciales | Existe solo el reporte 1 (P-01). |
| Pasos | 1. Como Andrés (4), ejecutar `POST /reportes` con cada cuerpo inválido (a, b, c, d).<br>2. Como Carolina (1), ejecutar `GET /reportes`. |
| Datos de entrada | `X-Usuario-Id: 4`<br>a) Sin espacio: `{"tipo_falla": "iluminacion", "descripcion": "Sin espacio"}`<br>b) Tipo inválido: `{"espacio_id": 3, "tipo_falla": "agua", "descripcion": "Tipo inválido"}`<br>c) Descripción vacía: `{"espacio_id": 3, "tipo_falla": "otro", "descripcion": "   "}`<br>d) Espacio inexistente: `{"espacio_id": 999, "tipo_falla": "otro", "descripcion": "Espacio inexistente"}` |
| Método y código HTTP esperado | 1. `POST /reportes` → **422** en los cuatro casos<br>2. `GET /reportes` → **200** |
| Resultado esperado | Cada intento se rechaza con un mensaje claro en `detail`:<br>a) "el campo 'espacio_id' es obligatorio"<br>b) "el campo 'tipo_falla' debe ser uno de: …"<br>c) "el campo 'descripcion' no puede estar vacío"<br>d) "El espacio indicado no existe"<br>La lista sigue teniendo solo el reporte `[1]`: no se creó ningún registro inválido. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-03

| Campo | Valor |
|---|---|
| Identificador | P-03 |
| Prueba | Consulta de reportes y detalle de un reporte |
| Requisito relacionado | RF-03, RF-04, RN-10 (CA-01) |
| Condiciones iniciales | Existe el reporte 1, creado por Andrés (P-01). |
| Pasos | 1. Como Andrés (4), ejecutar `GET /reportes`.<br>2. Como Andrés (4), ejecutar `GET /reportes/1`.<br>3. Como Sofía (5), ejecutar `GET /reportes`. |
| Datos de entrada | `X-Usuario-Id: 4` y luego `X-Usuario-Id: 5` |
| Método y código HTTP esperado | 1. `GET /reportes` → **200**<br>2. `GET /reportes/1` → **200**<br>3. `GET /reportes` → **200** |
| Resultado esperado | 1. Andrés ve la lista con el reporte 1.<br>2. El detalle trae los datos guardados: espacio "Laboratorio de Química" con su ubicación, reportante "Andrés Torres", estado `reportado` y lista de intervenciones vacía.<br>3. Sofía recibe una lista vacía `[]`, porque solo ve sus propios reportes. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-04

| Campo | Valor |
|---|---|
| Identificador | P-04 |
| Prueba | Consulta de un reporte inexistente |
| Requisito relacionado | RF-04, RNF-04 |
| Condiciones iniciales | No existe un reporte con id 999. |
| Pasos | 1. Como Carolina (1), ejecutar `GET /reportes/999`. |
| Datos de entrada | `X-Usuario-Id: 1`, `reporte_id = 999` |
| Método y código HTTP esperado | `GET /reportes/999` → **404** |
| Resultado esperado | Respuesta controlada `{"detail": "Reporte no encontrado"}`, sin datos internos ni trazas de error. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-05

| Campo | Valor |
|---|---|
| Identificador | P-05 |
| Prueba | Evaluación y actualización válida de un reporte |
| Requisito relacionado | RF-05, RN-03 (CA-02) |
| Condiciones iniciales | El reporte 1 está en estado `reportado`. |
| Pasos | 1. Como Carolina (1), aprobar el reporte 1 con `PATCH /reportes/1/evaluacion`.<br>2. Como Sofía (5), crear el reporte 2 con `POST /reportes`.<br>3. Como Carolina (1), intentar rechazar el reporte 2 sin comentario.<br>4. Como Carolina (1), rechazar el reporte 2 con motivo. |
| Datos de entrada | 1. `X-Usuario-Id: 1`, `{"decision": "aprobar", "comentario": "Falla confirmada"}`<br>2. `X-Usuario-Id: 5`, `{"espacio_id": 1, "tipo_falla": "mobiliario", "descripcion": "Silla rota en la fila 3"}`<br>3. `X-Usuario-Id: 1`, `{"decision": "rechazar"}`<br>4. `X-Usuario-Id: 1`, `{"decision": "rechazar", "comentario": "Reporte repetido: la silla ya fue reportada"}` |
| Método y código HTTP esperado | 1. `PATCH /reportes/1/evaluacion` → **200**<br>2. `POST /reportes` → **201**<br>3. `PATCH /reportes/2/evaluacion` → **422**<br>4. `PATCH /reportes/2/evaluacion` → **200** |
| Resultado esperado | 1. El reporte 1 queda `aprobado`, con `comentario_decision` "Falla confirmada" y `fecha_evaluacion` registrada.<br>2. Se crea el reporte 2.<br>3. El rechazo sin motivo responde "El rechazo requiere un comentario con el motivo" y el reporte no cambia.<br>4. El reporte 2 queda `rechazado` con su motivo. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-06

| Campo | Valor |
|---|---|
| Identificador | P-06 |
| Prueba | Intento de transición de estado no permitida |
| Requisito relacionado | RF-05, RF-06, RN-03, RN-04, RN-07 (CA-02, CA-03) |
| Condiciones iniciales | El reporte 1 está `aprobado` y el reporte 2 está `rechazado` (P-05). |
| Pasos | Como Carolina (1):<br>a) Evaluar de nuevo el reporte 1, que ya no está `reportado`.<br>b) Asignar el reporte 2, que no está `aprobado`.<br>c) Aprobar el reporte 2; `rechazado` es un estado final.<br>d) Consultar `GET /reportes/1` y `GET /reportes/2`. |
| Datos de entrada | `X-Usuario-Id: 1`<br>a) `PATCH /reportes/1/evaluacion` con `{"decision": "rechazar", "comentario": "Cambio de opinión"}`<br>b) `PATCH /reportes/2/asignacion` con `{"responsable_id": 2}`<br>c) `PATCH /reportes/2/evaluacion` con `{"decision": "aprobar"}` |
| Método y código HTTP esperado | a) **409**<br>b) **409**<br>c) **409**<br>d) **200** |
| Resultado esperado | a) "No se puede evaluar un reporte que no está en estado reportado"<br>b) "No se puede asignar un reporte que no está aprobado"<br>c) "No se puede evaluar un reporte que no está en estado reportado"<br>d) Los estados no cambiaron: el reporte 1 sigue `aprobado` y el reporte 2 sigue `rechazado`. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-07

| Campo | Valor |
|---|---|
| Identificador | P-07 |
| Prueba | Asignación de un responsable autorizado |
| Requisito relacionado | RF-06, RN-04 (CA-03) |
| Condiciones iniciales | El reporte 1 está `aprobado`. |
| Pasos | 1. Como Carolina (1), intentar asignar el reporte 1 a un usuario que no es de mantenimiento.<br>2. Como Carolina (1), asignarlo a Mateo (2).<br>3. Como Mateo (2), ejecutar `GET /reportes`.<br>4. Como Andrés (4), ejecutar `GET /reportes/1`. |
| Datos de entrada | 1. `X-Usuario-Id: 1`, `{"responsable_id": 4}`<br>2. `X-Usuario-Id: 1`, `{"responsable_id": 2}`<br>3. `X-Usuario-Id: 2`<br>4. `X-Usuario-Id: 4` |
| Método y código HTTP esperado | 1. `PATCH /reportes/1/asignacion` → **422**<br>2. `PATCH /reportes/1/asignacion` → **200**<br>3. `GET /reportes` → **200**<br>4. `GET /reportes/1` → **200** |
| Resultado esperado | 1. "El responsable debe ser un usuario existente con rol mantenimiento".<br>2. El reporte 1 queda `asignado`, con responsable "Mateo Gómez" y `fecha_asignacion` registrada.<br>3. Mateo ve el reporte 1 en su lista `[1]`.<br>4. El reportante también ve al responsable en el detalle. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-08

| Campo | Valor |
|---|---|
| Identificador | P-08 |
| Prueba | Intento de gestión por un usuario no autorizado |
| Requisito relacionado | RF-13, RNF-02, RN-03 a RN-05, RN-10 (CA-02, CA-03, CA-04) |
| Condiciones iniciales | El reporte 1 está `asignado` a Mateo (2), sin intervenciones (P-07). |
| Pasos | a) Andrés (reportante) intenta evaluar el reporte 1.<br>b) Mateo (mantenimiento) intenta asignar el reporte 1.<br>c) Laura (mantenimiento, no responsable) intenta registrar una intervención.<br>d) Carolina (coordinación) intenta registrar una intervención.<br>e) Andrés intenta ver el resumen.<br>f) Se consulta la lista sin el encabezado `X-Usuario-Id`.<br>g) Sofía intenta ver el detalle de un reporte ajeno.<br>h) Carolina consulta el reporte 1. |
| Datos de entrada | a) `X-Usuario-Id: 4`, `PATCH /reportes/1/evaluacion`, `{"decision": "aprobar"}`<br>b) `X-Usuario-Id: 2`, `PATCH /reportes/1/asignacion`, `{"responsable_id": 3}`<br>c) `X-Usuario-Id: 3`, `POST /reportes/1/intervenciones`, `{"descripcion": "Intento de Laura"}`<br>d) `X-Usuario-Id: 1`, `POST /reportes/1/intervenciones`, `{"descripcion": "Intento de coordinación"}`<br>e) `X-Usuario-Id: 4`, `GET /reportes/resumen`<br>f) Sin encabezado, `GET /reportes`<br>g) `X-Usuario-Id: 5`, `GET /reportes/1`<br>h) `X-Usuario-Id: 1`, `GET /reportes/1` |
| Método y código HTTP esperado | a) a e) **403**<br>f) **401**<br>g) **404**<br>h) **200** |
| Resultado esperado | a) a e) "No tiene permiso para realizar esta acción"; en c) el mensaje es "Solo el responsable asignado puede realizar esta acción".<br>f) "Debe identificarse con un usuario válido".<br>g) "Reporte no encontrado": un reportante no ve reportes ajenos.<br>h) La información no se alteró: el reporte sigue `asignado` a Mateo y sin intervenciones. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-09

| Campo | Valor |
|---|---|
| Identificador | P-09 |
| Prueba | Registro de una intervención válida |
| Requisito relacionado | RF-07, RF-08, RN-05 (CA-04) |
| Condiciones iniciales | El reporte 1 está `asignado` a Mateo (2). |
| Pasos | Como Mateo (2):<br>1. Registrar la primera intervención.<br>2. Consultar `GET /reportes/1`.<br>3. Registrar una segunda intervención.<br>4. Intentar registrar una intervención con descripción vacía. |
| Datos de entrada | `X-Usuario-Id: 2`<br>1. `{"descripcion": "Se revisó la lámpara: balasto dañado"}`<br>3. `{"descripcion": "Se cambió el balasto"}`<br>4. `{"descripcion": ""}` |
| Método y código HTTP esperado | 1. `POST /reportes/1/intervenciones` → **201**<br>2. `GET /reportes/1` → **200**<br>3. `POST /reportes/1/intervenciones` → **201**<br>4. `POST /reportes/1/intervenciones` → **422** |
| Resultado esperado | 1. Se crea la intervención 1, con responsable "Mateo Gómez" y fecha automática.<br>2. Con la primera intervención el reporte pasa a `en_atencion` y el historial tiene 1 intervención.<br>3. Se crea la intervención 2; el estado sigue `en_atencion`.<br>4. "el campo 'descripcion' no puede estar vacío", sin crear registro. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-10

| Campo | Valor |
|---|---|
| Identificador | P-10 |
| Prueba | Cierre de un reporte y consulta de su resultado |
| Requisito relacionado | RF-09, RF-10, RF-08, RN-06, RN-07 (CA-05) |
| Condiciones iniciales | El reporte 1 está `en_atencion` con 2 intervenciones (P-09). |
| Pasos | 1. Como Mateo (2), intentar cerrar sin resultado.<br>2. Como Mateo (2), cerrar con resultado.<br>3. Como Andrés (4), consultar `GET /reportes/1`.<br>4. Como Mateo (2), intentar registrar otra intervención.<br>5. Como Mateo (2), intentar cerrar de nuevo. |
| Datos de entrada | 1. `X-Usuario-Id: 2`, `{"resultado": ""}`<br>2. `X-Usuario-Id: 2`, `{"resultado": "Lámpara reparada y funcionando"}`<br>3. `X-Usuario-Id: 4`<br>4. `X-Usuario-Id: 2`, `{"descripcion": "Otra más"}`<br>5. `X-Usuario-Id: 2`, `{"resultado": "Otro resultado"}` |
| Método y código HTTP esperado | 1. `PATCH /reportes/1/cierre` → **422**<br>2. `PATCH /reportes/1/cierre` → **200**<br>3. `GET /reportes/1` → **200**<br>4. `POST /reportes/1/intervenciones` → **409**<br>5. `PATCH /reportes/1/cierre` → **409** |
| Resultado esperado | 1. "El cierre requiere un resultado".<br>2. El reporte queda `cerrado`, con `resultado_cierre` y `fecha_cierre` registrados.<br>3. El reportante ve el estado `cerrado`, el resultado y el historial en orden cronológico: "Se revisó la lámpara: balasto dañado" y luego "Se cambió el balasto".<br>4 y 5. El reporte cerrado no admite cambios. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-11

| Campo | Valor |
|---|---|
| Identificador | P-11 |
| Prueba | Consulta de información consolidada |
| Requisito relacionado | RF-11, RF-12 (CA-06) |
| Condiciones iniciales | Reporte 1 `cerrado` (iluminación, espacio 3, responsable Mateo); reporte 2 `rechazado` (mobiliario, espacio 1). |
| Pasos | Como Carolina (1):<br>a) Consultar el resumen.<br>b) a g) Consultar la lista con cada filtro.<br>h) Consultar la lista sin filtros. |
| Datos de entrada | `X-Usuario-Id: 1`<br>a) `GET /reportes/resumen`<br>b) `estado=cerrado`<br>c) `estado=rechazado`<br>d) `tipo_falla=mobiliario`<br>e) `espacio_id=3`<br>f) `responsable_id=2`<br>g) `estado=cerrado` y `tipo_falla=iluminacion`<br>h) `GET /reportes` sin filtros |
| Método y código HTTP esperado | `GET /reportes/resumen` → **200**<br>`GET /reportes` con filtros → **200** |
| Resultado esperado | a) `{"reportado": 0, "aprobado": 0, "rechazado": 1, "asignado": 0, "en_atencion": 0, "cerrado": 1}`<br>b) `[1]`<br>c) `[2]`<br>d) `[2]`<br>e) `[1]`<br>f) `[1]`<br>g) `[1]`<br>h) `[1, 2]`<br>Los conteos coinciden con los reportes de la lista. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |

### P-12

| Campo | Valor |
|---|---|
| Identificador | P-12 |
| Prueba | Integración interfaz–API–base de datos |
| Requisito relacionado | RF-14, RNF-07, RF-01 a RF-11 (CA-01 a CA-05) |
| Condiciones iniciales | Pruebas P-01 a P-11 ejecutadas: existen los reportes 1 y 2. Servidor en marcha. Interfaz abierta en `http://127.0.0.1:8000/`, opcionalmente con las herramientas de desarrollador (F12, pestaña **Red**) para ver las solicitudes. |
| Pasos | 1. Ingresar como "Andrés Torres (Reportante)". En **Nuevo reporte**, elegir el espacio y el tipo, escribir la descripción y pulsar **Enviar reporte**.<br>2. Ingresar como "Carolina Ruiz (Coordinación)". En **Todos los reportes**, abrir el detalle del reporte 3, escribir el comentario y pulsar **Aprobar**. Luego elegir "Laura Pérez" y pulsar **Asignar**.<br>3. Ingresar como "Laura Pérez (Mantenimiento)". En **Mis asignados**, abrir el reporte 3, escribir la intervención y pulsar **Registrar intervención**. Luego escribir el resultado y pulsar **Cerrar**.<br>4. Ingresar como Andrés. En **Mis reportes**, abrir el reporte 3.<br>5. Detener el servidor (Ctrl+C), arrancarlo de nuevo y, en `/docs`, consultar `GET /reportes/3` como Carolina (1) y `GET /reportes/resumen`. |
| Datos de entrada | Espacio: "Sala de Cómputo 3"<br>Tipo: "Climatización"<br>Descripción: "El aire acondicionado no enfría"<br>Comentario: "Falla confirmada"<br>Intervención: "Se recargó el gas del equipo"<br>Resultado: "Aire acondicionado funcionando" |
| Método y código HTTP esperado | Solicitudes que hace la interfaz:<br>`POST /reportes` → **201**<br>`PATCH /reportes/3/evaluacion` → **200**<br>`PATCH /reportes/3/asignacion` → **200**<br>`POST /reportes/3/intervenciones` → **201**<br>`PATCH /reportes/3/cierre` → **200**<br>Tras reiniciar: `GET /reportes/3` → **200** y `GET /reportes/resumen` → **200** |
| Resultado esperado | En cada paso la interfaz muestra un mensaje de éxito y el nuevo estado: Reportado → Aprobado → Asignado → En atención → Cerrado. Cada rol ve solo las acciones que le corresponden. Andrés ve el resultado y el historial. Después de reiniciar el servidor, el reporte 3 sigue `cerrado`, con responsable "Laura Pérez", una intervención y su resultado. El resumen muestra `rechazado: 1` y `cerrado: 2`. |
| Resultado obtenido | |
| Estado (aprobada/fallida) | |
| Evidencia | |
