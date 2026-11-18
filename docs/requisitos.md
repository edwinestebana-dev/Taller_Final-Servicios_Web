# Requisitos: Sistema de reportes de fallas y mantenimiento de instalaciones

> Estado: BORRADOR del equipo, pendiente de revisión del docente.
> El docente no respondió a la solicitud de entrevista. Por eso las decisiones de este documento fueron tomadas por el equipo, eligiendo la opción más sencilla que cumple CA-01 a CA-06, y quedan registradas como **supuestos no confirmados** (sección 8).

## 1. Registro de entrevista y decisiones

- **Entrevista:** no realizada (sin respuesta del docente).
- **Fecha de las decisiones del equipo:** 17/11/2026
- **Criterio aplicado:** hacer solo lo que exige la guía; no incluir funciones recomendadas ni extras.

| # | Tema | Decisión del equipo | Estado |
|---|------|---------------------|--------|
| 1 | Quién reporta | Cualquier usuario con rol Reportante | Supuesto |
| 2 | Identificación de usuarios | Sin contraseñas: el usuario se elige de una lista de usuarios ficticios y el sistema toma su rol de la base de datos | Supuesto |
| 3 | Visibilidad del reportante | Ve solo sus propios reportes | Supuesto |
| 4 | Visibilidad de mantenimiento | Ve solo los reportes que le asignaron | Supuesto |
| 5 | Visibilidad de coordinación | Ve todos los reportes y el consolidado | Supuesto |
| 6 | Datos del reporte | Espacio, tipo de falla, descripción; fecha y reportante se registran automáticamente | Supuesto |
| 7 | Tipos de falla | Lista fija: Iluminación, Mobiliario, Climatización, Otro | Supuesto |
| 8 | Espacios y usuarios | Precargados con datos ficticios; no hay pantallas para administrarlos | Supuesto |
| 9 | Datos adicionales (prioridad, fotos, etc.) | Ninguno | Supuesto |
| 10 | Estados | Reportado, Aprobado, Rechazado, Asignado, En atención, Cerrado | Supuesto |
| 11 | Evaluación | La coordinación aprueba o rechaza; el rechazo exige motivo | Supuesto |
| 12 | Reapertura | No se contempla; Rechazado y Cerrado son estados finales | Supuesto |
| 13 | Transiciones prohibidas | Las no listadas en la sección 3 (por ejemplo, asignar sin aprobar o cerrar sin intervenciones) | Supuesto |
| 14 | Responsables por reporte | Uno solo | Supuesto |
| 15 | Reglas de asignación | Solo a usuarios con rol Mantenimiento; solo reportes Aprobados; no se reasigna | Supuesto |
| 16 | Datos de una intervención | Descripción; fecha y responsable se registran automáticamente | Supuesto |
| 17 | Cierre | Lo hace el responsable asignado; exige resultado; la fecha es automática | Supuesto |
| 18 | Reportes repetidos | La coordinación los detecta al evaluar y rechaza el repetido indicando el motivo | Supuesto |
| 19 | Consolidado | Conteo de reportes por estado y listado filtrable por estado, espacio, tipo y responsable | Supuesto |
| 20 | Historial | Se conserva el historial de intervenciones de cada reporte | Supuesto |
| 21 | Funciones fuera de la guía (fotos, correo, exportar, búsqueda por texto, paginación, gráficos) | No se implementan | Supuesto |

## 2. Actores y permisos

| Actor | Puede | No puede |
|-------|-------|----------|
| Reportante | Registrar fallas; consultar sus reportes y su detalle | Evaluar, asignar, registrar intervenciones, cerrar, ver reportes ajenos |
| Personal de mantenimiento | Consultar los reportes que le asignaron; registrar intervenciones; cerrar sus reportes | Evaluar, asignar, ver reportes no asignados a él |
| Coordinación | Ver todos los reportes; evaluar; asignar responsable; ver el consolidado | Registrar intervenciones, cerrar reportes |

## 3. Reglas de negocio

- **RN-01:** Un reporte requiere un espacio existente, un tipo de falla válido y una descripción no vacía.
- **RN-02:** Todo reporte nuevo queda en estado Reportado.
- **RN-03:** Solo la coordinación evalúa. Un reporte Reportado pasa a Aprobado o a Rechazado. El rechazo exige un motivo.
- **RN-04:** Solo se asigna un reporte Aprobado, a un usuario con rol Mantenimiento. No se reasigna.
- **RN-05:** Solo el responsable asignado registra intervenciones, cuando el reporte está Asignado o En atención. La primera intervención cambia el estado a En atención.
- **RN-06:** Solo el responsable asignado cierra el reporte, cuando está En atención y con un resultado informado.
- **RN-07:** Rechazado y Cerrado son estados finales.
- **RN-08:** Los reportes no se eliminan.
- **RN-09:** Un reporte repetido se rechaza con motivo; no existe vinculación automática.
- **RN-10:** Visibilidad: el reportante ve sus reportes, mantenimiento ve los asignados, coordinación ve todos.

### Transiciones de estado permitidas

| Desde | Hacia | Quién | Condición |
|-------|-------|-------|-----------|
| Reportado | Aprobado | Coordinación | Decisión de aprobar |
| Reportado | Rechazado | Coordinación | Motivo obligatorio |
| Aprobado | Asignado | Coordinación | Responsable con rol Mantenimiento |
| Asignado | En atención | Responsable asignado | Primera intervención registrada |
| En atención | Cerrado | Responsable asignado | Resultado informado |

Cualquier otra transición se rechaza.

## 4. Requisitos funcionales

| ID | Requisito | Condición |
|----|-----------|-----------|
| RF-01 | Registrar un reporte de falla asociado a un espacio | CA-01 |
| RF-02 | Consultar la lista de espacios disponibles | CA-01 |
| RF-03 | Consultar la lista de reportes según el rol del usuario | CA-01, CA-06 |
| RF-04 | Consultar el detalle de un reporte con ubicación, estado, decisión, responsable, intervenciones y cierre | CA-01, CA-05 |
| RF-05 | Evaluar un reporte (aprobar o rechazar con motivo) | CA-02 |
| RF-06 | Asignar un responsable a un reporte aprobado | CA-03 |
| RF-07 | Registrar una intervención sobre un reporte asignado | CA-04 |
| RF-08 | Mostrar el historial de intervenciones de un reporte en orden cronológico | CA-04 |
| RF-09 | Cerrar un reporte registrando el resultado | CA-05 |
| RF-10 | Consultar el resultado del cierre | CA-05 |
| RF-11 | Consultar el conteo de reportes por estado | CA-06 |
| RF-12 | Filtrar el listado de reportes por estado, espacio, tipo y responsable | CA-06 |
| RF-13 | Identificar al usuario y su rol para aplicar permisos | CA-02, CA-03 |
| RF-14 | Ofrecer una interfaz web para cada rol que cubra estas funciones | CA-01 a CA-06 |

## 5. Requisitos no funcionales

| ID | Requisito |
|----|-----------|
| RNF-01 | El servidor valida todas las entradas, sin depender de la interfaz |
| RNF-02 | Cada endpoint verifica el rol del usuario y responde con error de permiso cuando corresponde |
| RNF-03 | Los datos se guardan en una base de datos relacional con claves foráneas y restricciones |
| RNF-04 | La API usa códigos HTTP adecuados y mensajes de error que no revelan información sensible |
| RNF-05 | Se usan solo datos ficticios; no hay secretos en el repositorio y existe un `.env.example` |
| RNF-06 | El README permite instalar y ejecutar la solución de forma reproducible |
| RNF-07 | La interfaz, la API y la base de datos se comunican de verdad; no hay datos simulados |

## 6. Historias de usuario y criterios de aceptación

**HU-01 (CA-01).** Como reportante, quiero registrar una falla en un espacio, para que mantenimiento la atienda.
- Un reporte válido se guarda en estado Reportado y se puede consultar con su espacio.
- Un reporte sin espacio, sin tipo o sin descripción se rechaza y no se crea.

**HU-02 (CA-02).** Como coordinador, quiero aprobar o rechazar los reportes, para decidir cuáles se atienden.
- Al aprobar, el estado pasa a Aprobado.
- Al rechazar sin motivo, la operación falla; con motivo, el estado pasa a Rechazado.
- Un usuario sin rol de coordinación no puede evaluar.

**HU-03 (CA-03).** Como coordinador, quiero asignar un responsable a un reporte aprobado, para que alguien lo atienda.
- La asignación queda guardada y la ven los actores autorizados.
- No se puede asignar un reporte que no esté Aprobado ni a un usuario que no sea de Mantenimiento.

**HU-04 (CA-04).** Como personal de mantenimiento, quiero registrar intervenciones, para dejar constancia del avance.
- Cada intervención queda ligada al reporte y se muestra en el historial.
- Solo el responsable asignado puede registrarlas.

**HU-05 (CA-05).** Como personal de mantenimiento, quiero cerrar la atención con su resultado, para finalizar el caso.
- El cierre exige que haya intervenciones y un resultado.
- Después del cierre, el reporte y su resultado se pueden consultar y no se pueden modificar.

**HU-06 (CA-06).** Como coordinador, quiero ver el consolidado de reportes, para supervisar la atención.
- Se muestran los conteos por estado, coherentes con los datos guardados.
- Se puede filtrar el listado por estado, espacio, tipo y responsable.

## 7. Priorización y alcance

- **Alcance (todo prioritario):** RF-01 a RF-14, que cubren CA-01 a CA-06 completos.
- **Fuera de alcance:** fotos adjuntas, notificaciones, exportación, búsqueda por texto, paginación, gráficos, prioridad del reporte, reasignación, reapertura, administración de espacios y usuarios, y todo lo que la guía excluye (inventario, compras, costos, IoT, contratos, SMS/WhatsApp, integración institucional).

## 8. Supuestos no confirmados

Todas las decisiones de la sección 1 son supuestos del equipo, porque el docente no respondió. Los de mayor impacto son:

- **S-01:** Basta con identificar al usuario por una lista, sin contraseñas.
- **S-02:** El responsable asignado es quien cierra el reporte.
- **S-03:** Los reportes repetidos se resuelven rechazándolos con motivo.
- **S-04:** El "historial" exigido es el de intervenciones, no el de cada cambio de estado.
- **S-05:** Los espacios y usuarios son datos ficticios precargados, sin pantallas de administración.

Si el docente responde y corrige alguno, se actualiza este documento y lo que dependa de él.

## 9. Aprobación del docente

- Fecha de aprobación: pendiente
- Observaciones:
