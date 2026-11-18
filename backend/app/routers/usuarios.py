"""Endpoint de usuarios (RF-13)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioSalida

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=list[UsuarioSalida])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista pública de usuarios para elegir con quién ingresar. No pide encabezado."""
    return db.scalars(select(Usuario).order_by(Usuario.id)).all()
