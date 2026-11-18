"""Reglas de negocio: qué se permite hacer y qué puede ver cada rol."""

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .models import Espacio, Reporte, Usuario
from .schemas import ReporteCrear


def crear_reporte(db: Session, datos: ReporteCrear, reportante: Usuario) -> Reporte:
    """Registra una falla (RF-01). El rol ya se verificó en el router."""
    # RN-01: el espacio debe existir. El tipo y la descripción ya los validó Pydantic.
    if db.get(Espacio, datos.espacio_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El espacio indicado no existe",
        )

    reporte = Reporte(
        espacio_id=datos.espacio_id,
        reportante_id=reportante.id,
        tipo_falla=datos.tipo_falla,
        descripcion=datos.descripcion,
        # El estado inicial "reportado" y la fecha los pone el modelo (RN-02).
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte


def reportes_visibles(usuario: Usuario) -> Select:
    """Consulta base según el rol (RN-10)."""
    consulta = select(Reporte)
    if usuario.rol == "reportante":
        consulta = consulta.where(Reporte.reportante_id == usuario.id)  # solo los suyos
    elif usuario.rol == "mantenimiento":
        consulta = consulta.where(Reporte.responsable_id == usuario.id)  # solo los asignados
    # Coordinación ve todos: no se agrega condición.
    return consulta


def listar_reportes(
    db: Session,
    usuario: Usuario,
    estado: str | None = None,
    espacio_id: int | None = None,
    tipo_falla: str | None = None,
    responsable_id: int | None = None,
) -> list[Reporte]:
    """Lista los reportes visibles para el usuario, con filtros opcionales (RF-03, RF-12)."""
    consulta = reportes_visibles(usuario)

    # Los filtros solo reducen lo que el usuario ya puede ver.
    if estado is not None:
        consulta = consulta.where(Reporte.estado == estado)
    if espacio_id is not None:
        consulta = consulta.where(Reporte.espacio_id == espacio_id)
    if tipo_falla is not None:
        consulta = consulta.where(Reporte.tipo_falla == tipo_falla)
    if responsable_id is not None:
        consulta = consulta.where(Reporte.responsable_id == responsable_id)

    return list(db.scalars(consulta.order_by(Reporte.id)))


def obtener_reporte_visible(db: Session, usuario: Usuario, reporte_id: int) -> Reporte:
    """Devuelve un reporte si existe y el usuario puede verlo; si no, responde 404."""
    reporte = db.scalar(reportes_visibles(usuario).where(Reporte.id == reporte_id))
    if reporte is None:
        # Mismo mensaje si no existe o si no es visible, para no revelar información.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado",
        )
    return reporte
