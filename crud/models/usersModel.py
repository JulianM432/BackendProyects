from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from db import engine

Base = declarative_base()


class User(Base):
    __tablename__ = "usuarios"

    nombre = Column(String)
    apellido = Column(String)
    dni = Column(Integer, primary_key=True)
    edad = Column(Integer)


Base.metadata.create_all(engine)
