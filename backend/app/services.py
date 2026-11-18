"""Reglas de negocio: qué se permite hacer y qué puede ver cada rol."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .models import ESTADOS, Espacio, Intervencion, Reporte, Usuario
from .schemas import (
    AsignacionEntrada,
    CierreEntrada,
    EvaluacionEntrada,
    IntervencionCrear,
    ReporteCrear,
)


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


# ---------- Ayudas para las acciones sobre un reporte ----------

def buscar_reporte(db: Session, reporte_id: int) -> Reporte:
    """Devuelve el reporte o responde 404 si no existe."""
    reporte = db.get(Reporte, reporte_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    return reporte


def exigir_estado(reporte: Reporte, estados_permitidos: tuple, mensaje: str) -> None:
    """Responde 409 si el estado actual no permite la transición."""
    if reporte.estado not in estados_permitidos:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)


def exigir_responsable(reporte: Reporte, usuario: Usuario) -> None:
    """Responde 403 si el usuario no es el responsable asignado del reporte."""
    if reporte.responsable_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el responsable asignado puede realizar esta acción",
        )


def datos_invalidos(mensaje: str) -> HTTPException:
    """Error 422 para reglas de datos que se revisan aquí y no en Pydantic."""
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=mensaje)


# ---------- Acciones (el rol ya se verificó en el router) ----------

def evaluar_reporte(db: Session, reporte_id: int, datos: EvaluacionEntrada) -> Reporte:
    """Aprueba o rechaza un reporte (RF-05, RN-03). Solo coordinación."""
    reporte = buscar_reporte(db, reporte_id)
    exigir_estado(reporte, ("reportado",), "No se puede evaluar un reporte que no está en estado reportado")

    comentario = (datos.comentario or "").strip()
    if datos.decision == "rechazar" and not comentario:
        raise datos_invalidos("El rechazo requiere un comentario con el motivo")

    reporte.estado = "aprobado" if datos.decision == "aprobar" else "rechazado"
    reporte.comentario_decision = comentario or None
    reporte.fecha_evaluacion = datetime.now()
    db.commit()
    db.refresh(reporte)
    return reporte


def asignar_responsable(db: Session, reporte_id: int, datos: AsignacionEntrada) -> Reporte:
    """Asigna un responsable de mantenimiento a un reporte aprobado (RF-06, RN-04). Solo coordinación."""
    reporte = buscar_reporte(db, reporte_id)
    # Al pasar a "asignado" ya no está "aprobado", por eso no se puede reasignar.
    exigir_estado(reporte, ("aprobado",), "No se puede asignar un reporte que no está aprobado")

    responsable = db.get(Usuario, datos.responsable_id)
    if responsable is None or responsable.rol != "mantenimiento":
        raise datos_invalidos("El responsable debe ser un usuario existente con rol mantenimiento")

    reporte.responsable_id = responsable.id
    reporte.fecha_asignacion = datetime.now()
    reporte.estado = "asignado"
    db.commit()
    db.refresh(reporte)
    return reporte


def registrar_intervencion(
    db: Session, reporte_id: int, datos: IntervencionCrear, usuario: Usuario
) -> Intervencion:
    """Registra una intervención (RF-07, RN-05). Solo el responsable asignado."""
    reporte = buscar_reporte(db, reporte_id)
    exigir_responsable(reporte, usuario)
    exigir_estado(
        reporte,
        ("asignado", "en_atencion"),
        "Solo se pueden registrar intervenciones en un reporte asignado o en atención",
    )

    intervencion = Intervencion(
        reporte_id=reporte.id,
        responsable_id=usuario.id,
        descripcion=datos.descripcion,
        # La fecha la pone el modelo.
    )
    db.add(intervencion)
    # La primera intervención cambia el estado a "en_atencion".
    if reporte.estado == "asignado":
        reporte.estado = "en_atencion"
    db.commit()
    db.refresh(intervencion)
    return intervencion


def cerrar_reporte(db: Session, reporte_id: int, datos: CierreEntrada, usuario: Usuario) -> Reporte:
    """Cierra el reporte con su resultado (RF-09, RN-06). Solo el responsable asignado."""
    reporte = buscar_reporte(db, reporte_id)
    exigir_responsable(reporte, usuario)
    # Estar "en_atencion" garantiza que ya hay al menos una intervención.
    exigir_estado(reporte, ("en_atencion",), "Solo se puede cerrar un reporte que está en atención")

    resultado = datos.resultado.strip()
    if not resultado:
        raise datos_invalidos("El cierre requiere un resultado")

    reporte.resultado_cierre = resultado
    reporte.fecha_cierre = datetime.now()
    reporte.estado = "cerrado"
    db.commit()
    db.refresh(reporte)
    return reporte


def contar_por_estado(db: Session) -> dict:
    """Conteo de reportes por estado (RF-11). Los estados sin reportes salen en 0."""
    conteo = {estado: 0 for estado in ESTADOS}
    filas = db.execute(select(Reporte.estado, func.count()).group_by(Reporte.estado))
    for estado, cantidad in filas:
        conteo[estado] = cantidad
    return conteo
