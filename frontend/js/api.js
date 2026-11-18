// Llamadas a la API REST con fetch. No hay datos simulados: todo viene del servidor.

// Id del usuario con el que se ingresó. Se envía en el encabezado X-Usuario-Id.
let usuarioActualId = null;

function fijarUsuario(id) {
  usuarioActualId = id;
}

// Hace la solicitud y devuelve el JSON. Si el servidor responde con error,
// lanza una excepción con el código y el mensaje "detail" que envió el servidor.
async function llamarApi(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (usuarioActualId !== null) {
    opciones.headers["X-Usuario-Id"] = String(usuarioActualId);
  }
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);
  }

  const respuesta = await fetch(ruta, opciones);
  const datos = await respuesta.json().catch(() => null);

  if (!respuesta.ok) {
    const detalle = datos && typeof datos.detail === "string" ? datos.detail : "Error inesperado";
    throw new Error(`Error ${respuesta.status}: ${detalle}`);
  }
  return datos;
}

// Arma "?estado=...&espacio_id=..." solo con los filtros que tienen valor.
function armarConsulta(filtros) {
  const parametros = new URLSearchParams();
  for (const [clave, valor] of Object.entries(filtros)) {
    if (valor !== "" && valor !== undefined && valor !== null) {
      parametros.append(clave, valor);
    }
  }
  const texto = parametros.toString();
  return texto ? `?${texto}` : "";
}

// Un método por endpoint de la sección 3 del diseño.
const api = {
  fijarUsuario,
  listarUsuarios: () => llamarApi("GET", "/usuarios"),
  listarEspacios: () => llamarApi("GET", "/espacios"),
  crearReporte: (datos) => llamarApi("POST", "/reportes", datos),
  listarReportes: (filtros = {}) => llamarApi("GET", "/reportes" + armarConsulta(filtros)),
  verResumen: () => llamarApi("GET", "/reportes/resumen"),
  verReporte: (id) => llamarApi("GET", `/reportes/${id}`),
  evaluar: (id, datos) => llamarApi("PATCH", `/reportes/${id}/evaluacion`, datos),
  asignar: (id, datos) => llamarApi("PATCH", `/reportes/${id}/asignacion`, datos),
  registrarIntervencion: (id, datos) => llamarApi("POST", `/reportes/${id}/intervenciones`, datos),
  cerrar: (id, datos) => llamarApi("PATCH", `/reportes/${id}/cierre`, datos),
};
