"""Endpoints de reportes. Las reglas están en services.py; aquí solo se recibe y se responde."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import services
from ..database import get_db
from ..models import Usuario
from ..schemas import Estado, ReporteCrear, ReporteDetalle, ReporteSalida, TipoFalla
from ..security import obtener_usuario_actual, requiere_rol

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.post("", response_model=ReporteSalida, status_code=status.HTTP_201_CREATED)
def crear_reporte(
    datos: ReporteCrear,
    usuario: Usuario = Depends(requiere_rol("reportante")),
    db: Session = Depends(get_db),
):
    """Registra una falla en un espacio (RF-01). Solo rol reportante."""
    return services.crear_reporte(db, datos, usuario)


@router.get("", response_model=list[ReporteSalida])
def listar_reportes(
    estado: Estado | None = None,
    espacio_id: int | None = None,
    tipo_falla: TipoFalla | None = None,
    responsable_id: int | None = None,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """Lista los reportes que el usuario puede ver, con filtros opcionales (RF-03, RF-12)."""
    return services.listar_reportes(db, usuario, estado, espacio_id, tipo_falla, responsable_id)


# Nota: cuando se agregue /reportes/resumen debe declararse antes de esta ruta.
@router.get("/{reporte_id}", response_model=ReporteDetalle)
def ver_reporte(
    reporte_id: int,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """Detalle de un reporte con espacio, decisión, responsable, intervenciones y cierre (RF-04, RF-08, RF-10)."""
    return services.obtener_reporte_visible(db, usuario, reporte_id)
