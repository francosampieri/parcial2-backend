"""Modelo persistente de generos."""
from sqlmodel import Field, Relationship, SQLModel

class Genero(SQLModel, table=True):
    __tablename__ = "genero"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    libros: list["Libro"] = Relationship(back_populates="genero")
