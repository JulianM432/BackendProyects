from typing import Optional

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

url = URL.create(
    drivername="postgresql",
    username="postgres",
    password="postgres",
    host="localhost",
    port=5432,
    database="utn",
)
engine = create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()

# SQLALCHEMY_DB_URL = "postgresql+psycopg2://postres:postgres@localhost:5432/utn"
Base = declarative_base()


def create_all():
    Base.metadata.create_all(bind=engine)


def drop_all():
    Base.metadata.drop_all(bind=engine)


def get_db():
    try:
        yield db
    finally:
        db.close()


class ContactoBd(Base):
    __tablename__ = "contactos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    direccion = Column(String(120))
    telefonos = Column(String(50))


create_all()


class ContactoModel(BaseModel):
    nombre: str
    direccion: Optional[str]
    telefono: Optional[str]


class Contacto(ContactoModel):
    id: int


@app.get("/")
async def get_root():
    return "<h1>Root</h1>"


@app.get("/contactos")
async def getAllContacts():
    return db.query(ContactoBd).all()


@app.post("/contactos")
async def addContact(unContacto: ContactoModel):
    contacto_db = ContactoBd()
    contacto_db.nombre = unContacto.nombre
    contacto_db.direccion = unContacto.direccion
    contacto_db.telefonos = unContacto.telefono
    db.add(contacto_db)
    db.commit()
    return {"message": "Usuario Creado"}

@app.delete("/contactos/{id}")
async def deleteContact(id: int):
    contacto = db.get(ContactoBd,id)
    if not contacto:
        return {"code":"id not found"}
    db.delete(contacto)
    db.commit()
    return {"code":"Contact Deleted"}