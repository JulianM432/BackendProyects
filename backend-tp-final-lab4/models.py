from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db import Base

class Cancha(Base):
    __tablename__ = "canchas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    techada = Column(Boolean, default=False)

    reservas = relationship("Reserva", back_populates="cancha")

    # def __init__(self, nombre, techada):
    #     self.nombre = nombre
    #     self.techada = techada

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    dia_hora = Column(DateTime, nullable=False) 
    duracion = Column(Integer, nullable=False)  
    nombre = Column(String(50), nullable=False)
    telefono = Column(Integer, nullable=False)

    cancha_id = Column(Integer, ForeignKey("canchas.id"), nullable=False)
    cancha = relationship("Cancha", back_populates="reservas")
    # def __init__(self, dia_hora, duracion, nombre, telefono, cancha):
    #     self.dia_hora = dia_hora
    #     self.duracion = duracion
    #     self.nombre = nombre
    #     self.telefono = telefono
    #     self.cancha = cancha

