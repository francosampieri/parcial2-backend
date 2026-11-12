"""Contratos HTTP de ventas, separados de las tablas persistentes."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RenglonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    libro_id: int
    cantidad: int = Field(gt=0)


class VentaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cliente_id: int
    renglones: list[RenglonCreate] = Field(min_length=1)

    @field_validator("renglones")
    @classmethod
    def libros_unicos(cls, value: list[RenglonCreate]) -> list[RenglonCreate]:
        ids = [item.libro_id for item in value]
        if len(ids) != len(set(ids)):
            raise ValueError("Un libro no puede repetirse en la misma venta")
        return value


class ClienteEnVenta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class RenglonRead(BaseModel):
    libro_id: int
    titulo: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class VentaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: datetime
    total: Decimal
    cliente: ClienteEnVenta


class VentaDetail(VentaRead):
    renglones: list[RenglonRead]
