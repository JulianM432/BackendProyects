from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from data.db import Base


class Cancha(Base):
    __tablename__ = "canchas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    techada = Column(Boolean, default=False)

    reservas = relationship("Reserva", back_populates="cancha")
