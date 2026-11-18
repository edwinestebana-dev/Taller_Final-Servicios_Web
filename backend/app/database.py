"""Conexión y sesión de base de datos (SQLite con SQLAlchemy)."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Carga las variables del archivo .env de la raíz del proyecto, si existe.
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_PROYECTO / ".env")

# Si no hay .env se usa un archivo reportes.db en la carpeta desde donde se ejecuta (backend/).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reportes.db")

# check_same_thread=False permite que FastAPI use la conexión desde distintos hilos.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def activar_claves_foraneas(conexion, _registro):
    """SQLite no valida las claves foráneas por defecto: se activan en cada conexión."""
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


# Fábrica de sesiones: cada solicitud trabajará con su propia sesión.
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos (tablas)."""


def get_db():
    """Entrega una sesión a cada endpoint y la cierra al terminar la solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
