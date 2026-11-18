// Pantallas y eventos de la página. Los permisos los decide el servidor;
// aquí solo se muestran las acciones que tienen sentido para el rol y el estado.

// ---------- Textos para mostrar ----------
const NOMBRES_ESTADO = {
  reportado: "Reportado",
  aprobado: "Aprobado",
  rechazado: "Rechazado",
  asignado: "Asignado",
  en_atencion: "En atención",
  cerrado: "Cerrado",
};
const NOMBRES_TIPO_FALLA = {
  iluminacion: "Iluminación",
  mobiliario: "Mobiliario",
  climatizacion: "Climatización",
  otro: "Otro",
};
const NOMBRES_ROL = {
  reportante: "Reportante",
  mantenimiento: "Mantenimiento",
  coordinacion: "Coordinación",
};

// Menú de cada rol: [texto del botón, función que dibuja la pantalla].
const MENUS = {
  reportante: [["Nuevo reporte", mostrarNuevoReporte], ["Mis reportes", () => mostrarLista()]],
  coordinacion: [["Todos los reportes", () => mostrarLista()], ["Resumen", mostrarResumen]],
  mantenimiento: [["Mis asignados", () => mostrarLista()]],
};

// ---------- Datos de la sesión (vienen de la API) ----------
const sesion = {
  usuario: null, // usuario con el que se ingresó
  usuarios: [], // lista de GET /usuarios
  espacios: [], // lista de GET /espacios
  filtros: {}, // últimos filtros usados en la lista
};

const selectorUsuario = document.getElementById("selector-usuario");
const menu = document.getElementById("menu");
const contenido = document.getElementById("contenido");
const mensaje = document.getElementById("mensaje");

// ---------- Utilidades ----------

// Evita que un texto escrito por un usuario se interprete como HTML.
function escapar(texto) {
  const reemplazos = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(texto ?? "").replace(/[&<>"']/g, (c) => reemplazos[c]);
}

function formatearFecha(fecha) {
  return fecha ? new Date(fecha).toLocaleString("es-CO") : "—";
}

function mostrarMensaje(texto, tipo = "error") {
  mensaje.textContent = texto;
  mensaje.className = `mensaje ${tipo}`;
}

function limpiarMensaje() {
  mensaje.textContent = "";
  mensaje.className = "mensaje oculto";
}

// Convierte el valor de un <select> en número; si está vacío no se envía el campo.
function numeroOVacio(valor) {
  return valor === "" || valor === null ? undefined : Number(valor);
}

// Arma las <option> de un <select> a partir de pares [valor, texto].
function opciones(pares, textoVacio, seleccionado = "") {
  const vacia = `<option value="">${escapar(textoVacio)}</option>`;
  return vacia + pares
    .map(([valor, texto]) => {
      const marcado = String(valor) === String(seleccionado) ? " selected" : "";
      return `<option value="${escapar(valor)}"${marcado}>${escapar(texto)}</option>`;
    })
    .join("");
}

function nombreEspacio(id) {
  const espacio = sesion.espacios.find((e) => e.id === id);
  return espacio ? espacio.nombre : `Espacio ${id}`;
}

function usuariosMantenimiento() {
  return sesion.usuarios.filter((u) => u.rol === "mantenimiento");
}

function etiquetaEstado(estado) {
  return `<span class="estado estado-${escapar(estado)}">${escapar(NOMBRES_ESTADO[estado] ?? estado)}</span>`;
}

// ---------- Ingreso ----------

async function iniciar() {
  try {
    sesion.usuarios = await api.listarUsuarios();
    selectorUsuario.innerHTML = opciones(
      sesion.usuarios.map((u) => [u.id, `${u.nombre} (${NOMBRES_ROL[u.rol]})`]),
      "Seleccione un usuario…"
    );
  } catch (error) {
    mostrarMensaje(error.message);
  }
}

async function ingresar() {
  limpiarMensaje();
  const id = numeroOVacio(selectorUsuario.value);
  sesion.usuario = sesion.usuarios.find((u) => u.id === id) ?? null;
  sesion.filtros = {};
  api.fijarUsuario(sesion.usuario ? sesion.usuario.id : null);

  if (!sesion.usuario) {
    menu.innerHTML = "";
    contenido.innerHTML = "<p>Elija un usuario en «Ingresar como» para comenzar.</p>";
    return;
  }

  try {
    sesion.espacios = await api.listarEspacios();
  } catch (error) {
    mostrarMensaje(error.message);
    return;
  }
  dibujarMenu();
  MENUS[sesion.usuario.rol][0][1](); // abre la primera pantalla del menú
}

function dibujarMenu() {
  const opcionesMenu = MENUS[sesion.usuario.rol];
  menu.innerHTML = opcionesMenu
    .map(([texto], i) => `<button type="button" data-opcion="${i}">${escapar(texto)}</button>`)
    .join("");
  menu.querySelectorAll("button").forEach((boton) => {
    boton.addEventListener("click", () => {
      limpiarMensaje();
      opcionesMenu[boton.dataset.opcion][1]();
    });
  });
}

// ---------- Pantalla: Nuevo reporte (reportante) ----------

function mostrarNuevoReporte() {
  contenido.innerHTML = `
    <h2>Nuevo reporte</h2>
    <form id="form-reporte" class="formulario">
      <label>Espacio
        <select name="espacio_id">
          ${opciones(sesion.espacios.map((e) => [e.id, `${e.nombre} — ${e.ubicacion}`]), "Seleccione un espacio…")}
        </select>
      </label>
      <label>Tipo de falla
        <select name="tipo_falla">
          ${opciones(Object.entries(NOMBRES_TIPO_FALLA), "Seleccione un tipo…")}
        </select>
      </label>
      <label>Descripción
        <textarea name="descripcion" rows="4"></textarea>
      </label>
      <button type="submit">Enviar reporte</button>
    </form>`;

  document.getElementById("form-reporte").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const datos = new FormData(evento.target);
    try {
      const reporte = await api.crearReporte({
        espacio_id: numeroOVacio(datos.get("espacio_id")),
        tipo_falla: datos.get("tipo_falla") || undefined,
        descripcion: datos.get("descripcion"),
      });
      await mostrarDetalle(reporte.id);
      mostrarMensaje(`Reporte #${reporte.id} registrado.`, "exito");
    } catch (error) {
      mostrarMensaje(error.message); // el formulario conserva lo escrito
    }
  });
}

// ---------- Pantalla: Lista de reportes (todos los roles) ----------

const TITULOS_LISTA = {
  reportante: "Mis reportes",
  mantenimiento: "Mis asignados",
  coordinacion: "Todos los reportes",
};

async function mostrarLista(filtros = sesion.filtros) {
  sesion.filtros = filtros;
  let reportes;
  try {
    reportes = await api.listarReportes(filtros);
  } catch (error) {
    mostrarMensaje(error.message);
    return;
  }

  // Los filtros solo se muestran a coordinación (sección 5 del diseño).
  const formularioFiltros = sesion.usuario.rol === "coordinacion" ? `
    <form id="form-filtros" class="filtros">
      <label>Estado
        <select name="estado">${opciones(Object.entries(NOMBRES_ESTADO), "Todos", filtros.estado)}</select>
      </label>
      <label>Espacio
        <select name="espacio_id">${opciones(sesion.espacios.map((e) => [e.id, e.nombre]), "Todos", filtros.espacio_id)}</select>
      </label>
      <label>Tipo
        <select name="tipo_falla">${opciones(Object.entries(NOMBRES_TIPO_FALLA), "Todos", filtros.tipo_falla)}</select>
      </label>
      <label>Responsable
        <select name="responsable_id">${opciones(usuariosMantenimiento().map((u) => [u.id, u.nombre]), "Todos", filtros.responsable_id)}</select>
      </label>
      <button type="submit">Filtrar</button>
      <button type="button" id="limpiar-filtros" class="secundario">Quitar filtros</button>
    </form>` : "";

  const filas = reportes.map((r) => `
    <tr>
      <td>${r.id}</td>
      <td>${escapar(nombreEspacio(r.espacio_id))}</td>
      <td>${escapar(NOMBRES_TIPO_FALLA[r.tipo_falla] ?? r.tipo_falla)}</td>
      <td>${etiquetaEstado(r.estado)}</td>
      <td><button type="button" class="secundario" data-id="${r.id}">Ver detalle</button></td>
    </tr>`).join("");

  contenido.innerHTML = `
    <h2>${TITULOS_LISTA[sesion.usuario.rol]}</h2>
    ${formularioFiltros}
    ${reportes.length === 0 ? "<p>No hay reportes para mostrar.</p>" : `
      <div class="tabla-contenedor">
        <table>
          <thead><tr><th>Id</th><th>Espacio</th><th>Tipo</th><th>Estado</th><th>Detalle</th></tr></thead>
          <tbody>${filas}</tbody>
        </table>
      </div>`}`;

  contenido.querySelectorAll("button[data-id]").forEach((boton) => {
    boton.addEventListener("click", () => {
      limpiarMensaje();
      mostrarDetalle(Number(boton.dataset.id));
    });
  });

  const form = document.getElementById("form-filtros");
  if (form) {
    form.addEventListener("submit", (evento) => {
      evento.preventDefault();
      limpiarMensaje();
      mostrarLista(Object.fromEntries(new FormData(form)));
    });
    document.getElementById("limpiar-filtros").addEventListener("click", () => {
      limpiarMensaje();
      mostrarLista({});
    });
  }
}

// ---------- Pantalla: Detalle de un reporte ----------

async function mostrarDetalle(id) {
  let r;
  try {
    r = await api.verReporte(id);
  } catch (error) {
    mostrarMensaje(error.message);
    return;
  }

  const decision = r.fecha_evaluacion
    ? `${r.estado === "rechazado" ? "Rechazado" : "Aprobado"} el ${formatearFecha(r.fecha_evaluacion)}
       ${r.comentario_decision ? `<br>Comentario: ${escapar(r.comentario_decision)}` : ""}`
    : "Pendiente de evaluación.";

  const responsable = r.responsable
    ? `${escapar(r.responsable.nombre)} (asignado el ${formatearFecha(r.fecha_asignacion)})`
    : "Sin asignar.";

  const cierre = r.fecha_cierre
    ? `Cerrado el ${formatearFecha(r.fecha_cierre)}<br>Resultado: ${escapar(r.resultado_cierre)}`
    : "Sin cerrar.";

  const historial = r.intervenciones.length === 0
    ? "<p>Sin intervenciones.</p>"
    : `<div class="tabla-contenedor"><table>
        <thead><tr><th>Fecha</th><th>Responsable</th><th>Descripción</th></tr></thead>
        <tbody>${r.intervenciones.map((i) => `
          <tr>
            <td>${formatearFecha(i.fecha)}</td>
            <td>${escapar(i.responsable.nombre)}</td>
            <td>${escapar(i.descripcion)}</td>
          </tr>`).join("")}</tbody>
      </table></div>`;

  contenido.innerHTML = `
    <h2>Reporte #${r.id} ${etiquetaEstado(r.estado)}</h2>
    <dl class="datos">
      <dt>Espacio</dt><dd>${escapar(r.espacio.nombre)} (${escapar(r.espacio.tipo)})</dd>
      <dt>Ubicación</dt><dd>${escapar(r.espacio.ubicacion)}</dd>
      <dt>Tipo de falla</dt><dd>${escapar(NOMBRES_TIPO_FALLA[r.tipo_falla] ?? r.tipo_falla)}</dd>
      <dt>Descripción</dt><dd>${escapar(r.descripcion)}</dd>
      <dt>Reportado por</dt><dd>${escapar(r.reportante.nombre)} el ${formatearFecha(r.fecha_creacion)}</dd>
      <dt>Decisión</dt><dd>${decision}</dd>
      <dt>Responsable</dt><dd>${responsable}</dd>
      <dt>Cierre</dt><dd>${cierre}</dd>
    </dl>
    <h3>Historial de intervenciones</h3>
    ${historial}
    <div id="acciones"></div>
    <p><button type="button" id="volver" class="secundario">Volver a la lista</button></p>`;

  document.getElementById("volver").addEventListener("click", () => {
    limpiarMensaje();
    mostrarLista();
  });
  dibujarAcciones(r);
}

// Muestra solo las acciones que corresponden al rol y al estado.
// Aunque alguien las invoque de otra forma, el servidor vuelve a verificarlo todo.
function dibujarAcciones(r) {
  const contenedor = document.getElementById("acciones");
  const rol = sesion.usuario.rol;
  const esResponsable = r.responsable !== null && r.responsable.id === sesion.usuario.id;
  let html = "";

  if (rol === "coordinacion" && r.estado === "reportado") {
    html += `
      <form id="form-evaluacion" class="formulario accion">
        <h3>Evaluar</h3>
        <label>Comentario (obligatorio para rechazar)
          <textarea name="comentario" rows="2"></textarea>
        </label>
        <div class="botones">
          <button type="submit" value="aprobar">Aprobar</button>
          <button type="submit" value="rechazar" class="peligro">Rechazar</button>
        </div>
      </form>`;
  }

  if (rol === "coordinacion" && r.estado === "aprobado") {
    html += `
      <form id="form-asignacion" class="formulario accion">
        <h3>Asignar responsable</h3>
        <label>Responsable
          <select name="responsable_id">
            ${opciones(usuariosMantenimiento().map((u) => [u.id, u.nombre]), "Seleccione un responsable…")}
          </select>
        </label>
        <button type="submit">Asignar</button>
      </form>`;
  }

  if (rol === "mantenimiento" && esResponsable && (r.estado === "asignado" || r.estado === "en_atencion")) {
    html += `
      <form id="form-intervencion" class="formulario accion">
        <h3>Registrar intervención</h3>
        <label>Descripción
          <textarea name="descripcion" rows="2"></textarea>
        </label>
        <button type="submit">Registrar intervención</button>
      </form>`;
  }

  if (rol === "mantenimiento" && esResponsable && r.estado === "en_atencion") {
    html += `
      <form id="form-cierre" class="formulario accion">
        <h3>Cerrar reporte</h3>
        <label>Resultado
          <textarea name="resultado" rows="2"></textarea>
        </label>
        <button type="submit">Cerrar</button>
      </form>`;
  }

  contenedor.innerHTML = html;

  // Cada formulario llama a su endpoint; si va bien se recarga el detalle.
  conectarAccion("form-evaluacion", (datos, boton) =>
    api.evaluar(r.id, { decision: boton.value, comentario: datos.get("comentario") }),
    (boton) => (boton.value === "aprobar" ? "Reporte aprobado." : "Reporte rechazado."));

  conectarAccion("form-asignacion", (datos) =>
    api.asignar(r.id, { responsable_id: numeroOVacio(datos.get("responsable_id")) }),
    () => "Responsable asignado.");

  conectarAccion("form-intervencion", (datos) =>
    api.registrarIntervencion(r.id, { descripcion: datos.get("descripcion") }),
    () => "Intervención registrada.");

  conectarAccion("form-cierre", (datos) =>
    api.cerrar(r.id, { resultado: datos.get("resultado") }),
    () => "Reporte cerrado.");

  function conectarAccion(idFormulario, llamar, textoExito) {
    const form = document.getElementById(idFormulario);
    if (!form) return;
    form.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      const boton = evento.submitter; // botón que se presionó (Aprobar o Rechazar)
      try {
        await llamar(new FormData(form), boton);
        await mostrarDetalle(r.id);
        mostrarMensaje(textoExito(boton), "exito");
      } catch (error) {
        mostrarMensaje(error.message); // error del servidor, el formulario conserva lo escrito
      }
    });
  }
}

// ---------- Pantalla: Resumen (coordinación) ----------

async function mostrarResumen() {
  let resumen;
  try {
    resumen = await api.verResumen();
  } catch (error) {
    mostrarMensaje(error.message);
    return;
  }
  const filas = Object.entries(resumen)
    .map(([estado, cantidad]) => `<tr><td>${etiquetaEstado(estado)}</td><td>${cantidad}</td></tr>`)
    .join("");
  contenido.innerHTML = `
    <h2>Resumen de reportes por estado</h2>
    <div class="tabla-contenedor">
      <table class="resumen">
        <thead><tr><th>Estado</th><th>Cantidad</th></tr></thead>
        <tbody>${filas}</tbody>
      </table>
    </div>`;
}

// ---------- Arranque ----------
selectorUsuario.addEventListener("change", ingresar);
iniciar();
