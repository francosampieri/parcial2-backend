"""Contratos HTTP separados de las tablas de clientes."""
from pydantic import BaseModel, ConfigDict, field_validator


class ClienteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str
    email: str


class ClienteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = None
    email: str | None = None

    @field_validator("nombre", "email", mode="before")
    @classmethod
    def no_nulos(cls, value: object) -> object:
        if value is None:
            raise ValueError("El campo no admite null")
        return value


class ClienteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: str
    perfil: "PerfilRead | None" = None


class PerfilRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    telefono: str
    direccion: str


class PerfilCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefono: str
    direccion: str
