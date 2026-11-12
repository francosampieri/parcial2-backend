"""Contratos de libros para el catálogo."""
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.modules.editoriales.schemas import EditorialRead


class GeneroEnLibro(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class LibroRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial: EditorialRead
    genero: GeneroEnLibro | None


class AutorEnLibro(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    nacionalidad: str


class AutoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    autor: AutorEnLibro
    rol: str
    orden: int


class LibroDetail(LibroRead):
    autores: list[AutoriaRead]


class AutoriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    autor_id: int
    rol: Literal["autor", "coautor", "traductor", "ilustrador"]
    orden: int = Field(ge=1)


class LibroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    isbn: str
    titulo: str
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    editorial_id: int
    genero_id: int | None = None
    autores: list[AutoriaCreate] = Field(min_length=1)

    @field_validator("precio")
    @classmethod
    def max_dos_decimales(cls, value: Decimal) -> Decimal:
        if value.as_tuple().exponent < -2:
            raise ValueError("El precio admite hasta dos decimales")
        return value


class LibroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    isbn: str | None = None
    titulo: str | None = None
    precio: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    editorial_id: int | None = None
    genero_id: int | None = None

    @field_validator("isbn", "titulo", "precio", "stock", "editorial_id", mode="before")
    @classmethod
    def no_nulos(cls, value):
        if value is None:
            raise ValueError("El campo no admite null")
        return value

    @field_validator("precio")
    @classmethod
    def max_dos_decimales(cls, value: Decimal) -> Decimal:
        if value.as_tuple().exponent < -2:
            raise ValueError("El precio admite hasta dos decimales")
        return value
