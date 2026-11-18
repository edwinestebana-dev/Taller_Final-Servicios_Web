"""Tablas de la base de datos (sección 2 de docs/diseno.md)."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# Valores permitidos, según el diseño.
ROLES = ("reportante", "mantenimiento", "coordinacion")
TIPOS_FALLA = ("iluminacion", "mobiliario", "climatizacion", "otro")
ESTADOS = ("reportado", "aprobado", "rechazado", "asignado", "en_atencion", "cerrado")


def valores_permitidos(columna: str, valores: tuple) -> str:
    """Arma la condición SQL "columna IN ('a', 'b', ...)" para un CHECK."""
    lista = ", ".join(f"'{valor}'" for valor in valores)
    return f"{columna} IN ({lista})"


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(valores_permitidos("rol", ROLES), name="ck_usuarios_rol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)


class Espacio(Base):
    __tablename__ = "espacios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)  # aula, oficina, laboratorio, zona común
    ubicacion: Mapped[str] = mapped_column(String(100), nullable=False)  # edificio y piso


class Reporte(Base):
    __tablename__ = "reportes"
    __table_args__ = (
        CheckConstraint(valores_permitidos("tipo_falla", TIPOS_FALLA), name="ck_reportes_tipo_falla"),
        CheckConstraint(valores_permitidos("estado", ESTADOS), name="ck_reportes_estado"),
        CheckConstraint("trim(descripcion) <> ''", name="ck_reportes_descripcion_no_vacia"),
        # El comentario de la decisión es obligatorio cuando el reporte se rechaza.
        CheckConstraint(
            "estado <> 'rechazado' OR trim(coalesce(comentario_decision, '')) <> ''",
            name="ck_reportes_rechazo_con_motivo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("espacios.id"), nullable=False)
    reportante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo_falla: Mapped[str] = mapped_column(String(20), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    # Todo reporte nuevo queda en estado "reportado" (RN-02).
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="reportado")
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    # Evaluación (se llenan al aprobar o rechazar).
    comentario_decision: Mapped[str | None] = mapped_column(Text)
    fecha_evaluacion: Mapped[datetime | None] = mapped_column(DateTime)

    # Asignación (se llenan al asignar el responsable).
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_asignacion: Mapped[datetime | None] = mapped_column(DateTime)

    # Cierre (se llenan al cerrar).
    resultado_cierre: Mapped[str | None] = mapped_column(Text)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones para consultar los datos ligados al reporte.
    # Hay dos claves foráneas hacia usuarios, por eso se indica cuál usa cada relación.
    espacio: Mapped["Espacio"] = relationship()
    reportante: Mapped["Usuario"] = relationship(foreign_keys=[reportante_id])
    responsable: Mapped["Usuario | None"] = relationship(foreign_keys=[responsable_id])
    # Historial de intervenciones en orden cronológico (RF-08).
    intervenciones: Mapped[list["Intervencion"]] = relationship(
        back_populates="reporte",
        order_by=lambda: (Intervencion.fecha, Intervencion.id),
    )


class Intervencion(Base):
    __tablename__ = "intervenciones"
    __table_args__ = (
        CheckConstraint("trim(descripcion) <> ''", name="ck_intervenciones_descripcion_no_vacia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reportes.id"), nullable=False)
    responsable_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    reporte: Mapped["Reporte"] = relationship(back_populates="intervenciones")
    responsable: Mapped["Usuario"] = relationship()
