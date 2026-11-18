"""Endpoint de espacios (RF-02)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Espacio, Usuario
from ..schemas import EspacioSalida
from ..security import obtener_usuario_actual

router = APIRouter(prefix="/espacios", tags=["Espacios"])


@router.get("", response_model=list[EspacioSalida])
def listar_espacios(
    _usuario: Usuario = Depends(obtener_usuario_actual),  # cualquier rol, pero identificado
    db: Session = Depends(get_db),
):
    """Lista de espacios disponibles para reportar fallas."""
    return db.scalars(select(Espacio).order_by(Espacio.id)).all()
