"""Contratos de entrada y salida de editoriales."""
from pydantic import BaseModel, ConfigDict, field_validator


class EditorialCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str
    pais: str


class EditorialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    pais: str


class EditorialUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = None
    pais: str | None = None

    @field_validator("nombre", "pais", mode="before")
    @classmethod
    def no_nulos(cls, value):
        if value is None:
            raise ValueError("El campo no admite null")
        return value
