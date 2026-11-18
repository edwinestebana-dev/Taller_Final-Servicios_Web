"""Esquemas Pydantic: validan lo que entra a la API y dan forma a lo que sale."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

# Valores permitidos (los mismos de models.py).
TipoFalla = Literal["iluminacion", "mobiliario", "climatizacion", "otro"]
Estado = Literal["reportado", "aprobado", "rechazado", "asignado", "en_atencion", "cerrado"]

# Texto obligatorio: se quitan los espacios de los extremos y no puede quedar vacío.
TextoNoVacio = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Salida(BaseModel):
    """Base de las respuestas: permite construirlas a partir de los modelos de SQLAlchemy."""

    model_config = ConfigDict(from_attributes=True)


# ---------- Usuarios y espacios ----------

class UsuarioSalida(Salida):
    id: int
    nombre: str
    rol: str


class EspacioSalida(Salida):
    id: int
    nombre: str
    tipo: str
    ubicacion: str


# ---------- Reportes ----------

class ReporteCrear(BaseModel):
    """Datos que envía el reportante. La fecha, el estado y el reportante los pone el servidor."""

    espacio_id: int
    tipo_falla: TipoFalla
    descripcion: TextoNoVacio


class ReporteSalida(Salida):
    """Reporte en la respuesta de creación y en el listado."""

    id: int
    espacio_id: int
    tipo_falla: str
    descripcion: str
    estado: str
    fecha_creacion: datetime


class IntervencionSalida(Salida):
    id: int
    descripcion: str
    fecha: datetime
    responsable: UsuarioSalida


class ReporteDetalle(Salida):
    """Detalle completo: espacio, decisión, responsable, intervenciones y cierre (RF-04)."""

    id: int
    tipo_falla: str
    descripcion: str
    estado: str
    fecha_creacion: datetime
    espacio: EspacioSalida
    reportante: UsuarioSalida
    # Evaluación
    comentario_decision: str | None
    fecha_evaluacion: datetime | None
    # Asignación
    responsable: UsuarioSalida | None
    fecha_asignacion: datetime | None
    # Cierre
    resultado_cierre: str | None
    fecha_cierre: datetime | None
    # Historial en orden cronológico (RF-08)
    intervenciones: list[IntervencionSalida]


# ---------- Acciones sobre un reporte ----------
# Pydantic revisa el formato (campos y tipos). Las reglas que dependen del estado
# del reporte se revisan en services.py, en el orden de la sección 4 del diseño.

class EvaluacionEntrada(BaseModel):
    decision: Literal["aprobar", "rechazar"]
    # Opcional al aprobar; al rechazar es obligatorio (se revisa en services.py).
    comentario: str | None = None


class AsignacionEntrada(BaseModel):
    responsable_id: int


class IntervencionCrear(BaseModel):
    descripcion: TextoNoVacio


class CierreEntrada(BaseModel):
    # Que no esté vacío se revisa en services.py, después del estado.
    resultado: str


class ResumenSalida(BaseModel):
    """Conteo de reportes por estado (RF-11)."""

    reportado: int
    aprobado: int
    rechazado: int
    asignado: int
    en_atencion: int
    cerrado: int
