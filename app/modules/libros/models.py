from typing import Optional
"""Modelos persistentes de libros y autorias."""
from decimal import Decimal
from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (CheckConstraint("precio > 0", name="ck_libro_precio"), CheckConstraint("stock >= 0", name="ck_libro_stock"))
    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True)
    titulo: str
    precio: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: int | None = Field(default=None, foreign_key="genero.id", index=True)
    editorial: "Editorial" = Relationship(back_populates="libros")
    genero: Optional["Genero"] = Relationship(back_populates="libros")
    autorias: list["LibroAutor"] = Relationship(back_populates="libro")
    renglones_venta: list["RenglonVenta"] = Relationship(back_populates="libro")

class LibroAutor(SQLModel, table=True):
    __tablename__ = "libro_autor"
    __table_args__ = (CheckConstraint("orden >= 1", name="ck_autoria_orden"), CheckConstraint("rol IN ('autor', 'coautor', 'traductor', 'ilustrador')", name="ck_autoria_rol"))
    libro_id: int = Field(primary_key=True, foreign_key="libro.id")
    autor_id: int = Field(primary_key=True, foreign_key="autor.id", index=True)
    rol: str
    orden: int
    libro: "Libro" = Relationship(back_populates="autorias")
    autor: "Autor" = Relationship(back_populates="autorias")

