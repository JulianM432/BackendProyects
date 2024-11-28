# uvicorn main:app --reload
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List
from db import Base, engine, get_db
from models import Cancha, Reserva
from pydantic import BaseModel

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Schemas para validación y serialización
class ReservaModel(BaseModel):
    dia_hora: datetime
    duracion: int
    nombre: str
    telefono: int
    cancha_id: int

    class Config:
        orm_mode = True


# class ReservaModelOut(ReservaModel):
#     id: int
#     class Config:
#         orm_mode = True


class CanchaModel(BaseModel):
    nombre: str
    techada: bool

    class Config:
        orm_mode = True


# class CanchaModelOut(CanchaModel):
#     id: int


def verificar_conflictos(unaReserva: ReservaModel, db: Session, reserva_id: int = None):
    # Obtener la cancha para verificar que exista
    cancha = db.query(Cancha).filter(Cancha.id == unaReserva.cancha_id).first()
    if not cancha:
        raise HTTPException(
            status_code=404,
            detail=f"La cancha con ID {unaReserva.cancha_id} no existe.",
        )
    try:

        # Verificar conflictos de horarios en las reservas existentes
        conflictos = (
            db.query(Reserva)
            .filter(
                Reserva.cancha_id == unaReserva.cancha_id,  # Misma cancha
                Reserva.id != reserva_id,  # Ignorar la reserva actual
                # Comparar las fechas y duraciones
                ( unaReserva.dia_hora < (Reserva.dia_hora + text(f"INTERVAL '{unaReserva.duracion} hours'")) ),
                ( (unaReserva.dia_hora + timedelta(hours=unaReserva.duracion)) > Reserva.dia_hora ),
            )
            .first()
        )
        # conflictos = (
        #     db.query(Reserva)
        #     .filter(
        #         Reserva.cancha_id == unaReserva.cancha_id,  # Misma cancha
        #         # Reserva.id != reserva_id,  # Ignorar la reserva actual
        #         # Comparar las fechas y duraciones correctamente
        #         ( unaReserva.dia_hora < (Reserva.dia_hora + timedelta(hours=Reserva.duracion)) ),
        #         ( (unaReserva.dia_hora + timedelta(hours=unaReserva.duracion)) > Reserva.dia_hora ),
        #     )
        #     .first()
        # )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: {e}")
    return conflictos


# Endpoints
@app.post("/reservas/", response_model=ReservaModel)
def crear_reserva(unaReserva: ReservaModel, db: Session = Depends(get_db)):
    conflictos = verificar_conflictos(unaReserva, db)
    if conflictos:
        raise HTTPException(
            status_code=400,
            detail="La reserva coincide con otra existente en la misma cancha.",
        )
    nueva_reserva = Reserva(**unaReserva.model_dump())
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return unaReserva
    # return nueva_reserva


@app.put("/reservas/{reserva_id}", response_model=ReservaModel)
def modificar_reserva(
    reserva_id: int, datos: ReservaModel, db: Session = Depends(get_db)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    # Actualizar campos modificados
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(reserva, key, value)
    # Verificar conflictos de horarios
    conflictos = verificar_conflictos(datos, db, reserva_id)
    if conflictos:
        raise HTTPException(
            status_code=400,
            detail="La reserva modificada coincide con otra existente en la misma cancha.",
        )

    db.commit()
    db.refresh(reserva)
    return reserva


@app.delete("/reservas/{reserva_id}")
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(reserva)
    db.commit()
    return {"detail": "Reserva eliminada correctamente"}


@app.get("/reservas/", response_model=List[ReservaModel])
def listar_reservas(cancha_id: int, dia: datetime, db: Session = Depends(get_db)):
    # Filtrar reservas por cancha y día
    inicio_dia = dia.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = inicio_dia + timedelta(days=1)
    cancha = db.query(Cancha).filter(Cancha.id == cancha_id).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.cancha_id == cancha_id,
            Reserva.dia_hora >= inicio_dia,
            Reserva.dia_hora < fin_dia,
        )
        .all()
    )

    return reservas


@app.get("/canchas", response_model=List[CanchaModel])
def listar_canchas(db: Session = Depends(get_db)):
    canchas = db.query(Cancha).all()
    return canchas


@app.post("/canchas/", response_model=CanchaModel)
def crear_cancha(unaCancha: CanchaModel, db: Session = Depends(get_db)):
    if unaCancha.nombre in [cancha.nombre for cancha in db.query(Cancha).all()]:
        raise HTTPException(status_code=400, detail="Nombre de cancha ya existente")
    db.add(Cancha(**unaCancha.model_dump()))
    db.commit()
    return unaCancha


@app.put("/canchas/{cancha_id}", response_model=CanchaModel)
def modificar_cancha(cancha_id: int, datos: CanchaModel, db: Session = Depends(get_db)):
    cancha = db.query(Cancha).filter(Cancha.id == cancha_id).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    # Actualizar campos modificados
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(cancha, key, value)
    db.commit()
    db.refresh(cancha)
    return cancha


@app.delete("/canchas/{cancha_id}")
def eliminar_cancha(cancha_id: int, db: Session = Depends(get_db)):
    cancha = db.query(Cancha).filter(Cancha.id == cancha_id).first()
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    db.delete(cancha)
    db.commit()
    return {"detail": "Cancha eliminada correctamente"}
