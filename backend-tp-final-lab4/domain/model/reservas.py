
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from data.db import Base

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    dia_hora = Column(DateTime, nullable=False) 
    duracion = Column(Integer, nullable=False)  
    nombre = Column(String(50), nullable=False)
    telefono = Column(Integer, nullable=False)

    cancha_id = Column(Integer, ForeignKey("canchas.id"), nullable=False)
    cancha = relationship("Cancha", back_populates="reservas")