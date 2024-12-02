from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Schemas para validación y serialización
class ReservaModel(BaseModel):
    dia_hora: datetime = Field(..., description="Fecha y hora de la reserva")
    duracion: int = Field(..., gt=0, description="Duración de la reserva en horas")
    nombre: str = Field(
        ..., min_length=3, description="Nombre de quien se hace la reserva"
    )
    telefono: int = Field(
        ..., description="Número de teléfono de quien se hace la reserva"
    )
    cancha_id: int = Field(..., gt=0, description="ID de la cancha")

    class Config:
        from_atributes = True


class ReservaUpdate(BaseModel):
    dia_hora: Optional[datetime] = Field(None, description="Fecha y hora de la reserva")
    duracion: Optional[int] = Field(
        None, gt=0, description="Duración de la reserva en horas"
    )
    nombre: Optional[str] = Field(
        None, min_length=3, description="Nombre de quien se hace la reserva"
    )
    telefono: Optional[int] = Field(
        None, description="Número de teléfono de quien se hace la reserva"
    )
    cancha_id: Optional[int] = Field(..., gt=0, description="ID de la cancha")
