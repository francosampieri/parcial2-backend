"""Contratos de entrada y salida de autores."""
from pydantic import BaseModel, ConfigDict, field_validator
from app.modules.libros.schemas import LibroRead


class AutorCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str
    nacionalidad: str


class AutorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    nacionalidad: str


class AutorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = None
    nacionalidad: str | None = None

    @field_validator("nombre", "nacionalidad", mode="before")
    @classmethod
    def no_nulos(cls, value):
        if value is None:
            raise ValueError("El campo no admite null")
        return value


class LibroDeAutor(LibroRead):
    rol: str
    orden: int
