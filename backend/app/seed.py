"""Carga datos ficticios iniciales: usuarios y espacios.

Uso (desde la carpeta backend/):  python -m app.seed
"""

from sqlalchemy import func, select

from .database import Base, SessionLocal, engine
from .models import Espacio, Usuario

# Usuarios ficticios: (nombre, rol)
USUARIOS = [
    ("Carolina Ruiz", "coordinacion"),
    ("Mateo Gómez", "mantenimiento"),
    ("Laura Pérez", "mantenimiento"),
    ("Andrés Torres", "reportante"),
    ("Sofía Ramírez", "reportante"),
]

# Espacios ficticios: (nombre, tipo, ubicación)
ESPACIOS = [
    ("Aula 101", "aula", "Bloque A, piso 1"),
    ("Aula 204", "aula", "Bloque A, piso 2"),
    ("Laboratorio de Química", "laboratorio", "Bloque B, piso 1"),
    ("Sala de Cómputo 3", "laboratorio", "Bloque C, piso 3"),
    ("Oficina de Coordinación", "oficina", "Bloque D, piso 2"),
    ("Cafetería Central", "zona común", "Bloque E, piso 1"),
]


def cargar_datos():
    # Crea las tablas si todavía no existen.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Si ya hay usuarios no se vuelve a cargar, para no duplicar datos.
        if db.scalar(select(func.count()).select_from(Usuario)) > 0:
            print("La base de datos ya tiene datos; no se cargó nada nuevo.")
            return

        db.add_all(Usuario(nombre=nombre, rol=rol) for nombre, rol in USUARIOS)
        db.add_all(
            Espacio(nombre=nombre, tipo=tipo, ubicacion=ubicacion)
            for nombre, tipo, ubicacion in ESPACIOS
        )
        db.commit()
        print(f"Datos cargados: {len(USUARIOS)} usuarios y {len(ESPACIOS)} espacios.")


if __name__ == "__main__":
    cargar_datos()
