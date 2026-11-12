"""Contratos de salida de salud; estas operaciones no reciben DTO de entrada."""
from typing import Literal

from pydantic import BaseModel


class LiveResponse(BaseModel):
    estado: Literal["vivo"] = "vivo"

class ReadyResponse(BaseModel):
    estado: Literal["listo"] = "listo"
