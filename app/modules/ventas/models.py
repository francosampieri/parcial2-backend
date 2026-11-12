"""Modelos persistentes de ventas y renglones."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

class Venta(SQLModel, table=True):
    __tablename__ = "venta"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_venta_total"),)
    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    fecha: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    total: Decimal = Field(max_digits=12, decimal_places=2)
    cliente: "Cliente" = Relationship(back_populates="ventas")
    renglones: list["RenglonVenta"] = Relationship(back_populates="venta")

class RenglonVenta(SQLModel, table=True):
    __tablename__ = "renglon_venta"
    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_renglon_cantidad"), CheckConstraint("precio_unitario > 0", name="ck_renglon_precio"))
    id: int | None = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    venta: "Venta" = Relationship(back_populates="renglones")
    libro: "Libro" = Relationship(back_populates="renglones_venta")

