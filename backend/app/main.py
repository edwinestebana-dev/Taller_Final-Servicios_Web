"""Punto de entrada de la aplicación: crea la app, las tablas y registra los routers.

Uso (desde la carpeta backend/):  uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import models  # noqa: F401  (importarlo registra las tablas en Base)
from .database import Base, engine
from .routers import espacios, reportes, usuarios

# Crea las tablas que falten al iniciar (no borra datos existentes).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reportes de fallas y mantenimiento",
    description="API para reportar fallas en instalaciones y gestionar su mantenimiento correctivo.",
    version="0.1.0",
)


def describir_error(error: dict) -> str:
    """Convierte un error de Pydantic en un mensaje corto en español."""
    tipo = error["type"]
    if tipo == "json_invalid":
        return "el cuerpo de la solicitud no es un JSON válido"

    # Nombre del campo sin la parte "body", "query" o "path".
    campo = ".".join(str(parte) for parte in error["loc"] if parte not in ("body", "query", "path"))
    nombre = f"el campo '{campo}'" if campo else "el cuerpo de la solicitud"

    if tipo == "missing":
        return f"{nombre} es obligatorio"
    if tipo == "string_too_short":
        return f"{nombre} no puede estar vacío"
    if tipo == "literal_error":
        permitidos = error["ctx"]["expected"].replace(" or ", ", ")
        return f"{nombre} debe ser uno de: {permitidos}"
    if tipo in ("int_parsing", "int_type", "int_from_float"):
        return f"{nombre} debe ser un número entero"
    if tipo == "string_type":
        return f"{nombre} debe ser texto"
    return f"{nombre} tiene un valor inválido"


@app.exception_handler(RequestValidationError)
async def responder_datos_invalidos(_request: Request, exc: RequestValidationError):
    """Responde 422 con el formato de error del diseño: {"detail": "mensaje"}."""
    mensajes = [describir_error(error) for error in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Datos inválidos: " + "; ".join(mensajes)},
    )


app.include_router(usuarios.router)
app.include_router(espacios.router)
app.include_router(reportes.router)


if __name__ == "__main__":
    # Permite arrancar también con:  python -m app.main
    import uvicorn

    uvicorn.run("app.main:app", reload=True)
