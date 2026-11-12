from typing import Optional
"""Modelos persistentes de clientes y perfiles."""
from sqlmodel import Field, Relationship, SQLModel

class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True)
    perfil: Optional["PerfilCliente"] = Relationship(back_populates="cliente")
    ventas: list["Venta"] = Relationship(back_populates="cliente")

class PerfilCliente(SQLModel, table=True):
    __tablename__ = "perfil_cliente"
    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(unique=True, foreign_key="cliente.id")
    telefono: str
    direccion: str
    cliente: "Cliente" = Relationship(back_populates="perfil")
