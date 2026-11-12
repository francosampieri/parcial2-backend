"""Modelo persistente de autores."""
from sqlmodel import Field, Relationship, SQLModel

class Autor(SQLModel, table=True):
    __tablename__ = "autor"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: str
    autorias: list["LibroAutor"] = Relationship(back_populates="autor")
