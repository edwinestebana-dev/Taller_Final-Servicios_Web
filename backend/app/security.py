"""Identifica al usuario con el encabezado X-Usuario-Id y verifica su rol."""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import Usuario


def obtener_usuario_actual(
    x_usuario_id: str | None = Header(
        default=None,
        alias="X-Usuario-Id",
        description="Id del usuario con el que se ingresa",
    ),
    db: Session = Depends(get_db),
) -> Usuario:
    """Busca al usuario del encabezado. El rol se toma de la base de datos, no del cliente."""
    try:
        usuario_id = int(x_usuario_id)
    except (TypeError, ValueError):
        # Falta el encabezado o no es un número: no hay usuario identificado.
        usuario_id = None

    usuario = db.get(Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe identificarse con un usuario válido",
        )
    return usuario


def requiere_rol(*roles_permitidos: str):
    """Crea una dependencia que solo deja pasar a los roles indicados (si no, responde 403)."""

    def verificar_rol(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para realizar esta acción",
            )
        return usuario

    return verificar_rol
