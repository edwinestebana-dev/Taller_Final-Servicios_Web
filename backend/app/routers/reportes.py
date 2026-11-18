"""Endpoints de reportes. Las reglas están en services.py; aquí solo se recibe y se responde."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import services
from ..database import get_db
from ..models import Usuario
from ..schemas import (
    AsignacionEntrada,
    CierreEntrada,
    Estado,
    EvaluacionEntrada,
    IntervencionCrear,
    IntervencionSalida,
    ReporteCrear,
    ReporteDetalle,
    ReporteSalida,
    ResumenSalida,
    TipoFalla,
)
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


# Se declara antes que /{reporte_id} para que "resumen" no se tome como un id.
@router.get("/resumen", response_model=ResumenSalida)
def ver_resumen(
    _usuario: Usuario = Depends(requiere_rol("coordinacion")),
    db: Session = Depends(get_db),
):
    """Conteo de reportes por estado (RF-11). Solo coordinación."""
    return services.contar_por_estado(db)


@router.get("/{reporte_id}", response_model=ReporteDetalle)
def ver_reporte(
    reporte_id: int,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """Detalle de un reporte con espacio, decisión, responsable, intervenciones y cierre (RF-04, RF-08, RF-10)."""
    return services.obtener_reporte_visible(db, usuario, reporte_id)


@router.patch("/{reporte_id}/evaluacion", response_model=ReporteDetalle)
def evaluar_reporte(
    reporte_id: int,
    datos: EvaluacionEntrada,
    _usuario: Usuario = Depends(requiere_rol("coordinacion")),
    db: Session = Depends(get_db),
):
    """Aprueba o rechaza un reporte en estado reportado (RF-05). Solo coordinación."""
    return services.evaluar_reporte(db, reporte_id, datos)


@router.patch("/{reporte_id}/asignacion", response_model=ReporteDetalle)
def asignar_responsable(
    reporte_id: int,
    datos: AsignacionEntrada,
    _usuario: Usuario = Depends(requiere_rol("coordinacion")),
    db: Session = Depends(get_db),
):
    """Asigna un responsable de mantenimiento a un reporte aprobado (RF-06). Solo coordinación."""
    return services.asignar_responsable(db, reporte_id, datos)


@router.post(
    "/{reporte_id}/intervenciones",
    response_model=IntervencionSalida,
    status_code=status.HTTP_201_CREATED,
)
def registrar_intervencion(
    reporte_id: int,
    datos: IntervencionCrear,
    usuario: Usuario = Depends(requiere_rol("mantenimiento")),
    db: Session = Depends(get_db),
):
    """Registra una intervención (RF-07). Solo el responsable asignado."""
    return services.registrar_intervencion(db, reporte_id, datos, usuario)


@router.patch("/{reporte_id}/cierre", response_model=ReporteDetalle)
def cerrar_reporte(
    reporte_id: int,
    datos: CierreEntrada,
    usuario: Usuario = Depends(requiere_rol("mantenimiento")),
    db: Session = Depends(get_db),
):
    """Cierra un reporte en atención con su resultado (RF-09). Solo el responsable asignado."""
    return services.cerrar_reporte(db, reporte_id, datos, usuario)
