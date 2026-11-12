"""Modelo persistente de editoriales."""
from sqlmodel import Field, Relationship, SQLModel

class Editorial(SQLModel, table=True):
    __tablename__ = "editorial"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    pais: str
    libros: list["Libro"] = Relationship(back_populates="editorial")
