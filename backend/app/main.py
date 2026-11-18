"""Punto de entrada de la aplicación.

Por ahora solo crea las tablas y arranca la API; los routers y el frontend
se agregan en los siguientes pasos.

Uso (desde la carpeta backend/):  uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from . import models  # noqa: F401  (importarlo registra las tablas en Base)
from .database import Base, engine

# Crea las tablas que falten al iniciar (no borra datos existentes).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reportes de fallas y mantenimiento",
    description="API para reportar fallas en instalaciones y gestionar su mantenimiento correctivo.",
    version="0.1.0",
)


if __name__ == "__main__":
    # Permite arrancar también con:  python -m app.main
    import uvicorn

    uvicorn.run("app.main:app", reload=True)
