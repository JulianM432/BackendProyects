from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from data.db import get_db
from api.models.reservas_models import ReservaModel, ReservaUpdate
from data.repositories.reservas_repo import ReservasRepo
from domain.exceptions.NotFound import NotFoundError
from domain.model.reservas import Reserva
from datetime import datetime

reservas_router = APIRouter(prefix="/reservas")
repo = ReservasRepo()


@reservas_router.get("/", response_model=List[ReservaModel])
def get_all(db: Session = Depends(get_db)):
    return repo.get_all(db)


@reservas_router.get("/{reserva_id}", response_model=ReservaModel)
def get_by_id(reserva_id: int, db: Session = Depends(get_db)):
    try:
        reserva = repo.get_by_id(db, reserva_id)
        return reserva
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada"
        )


@reservas_router.get("/cancha/{cancha_id}", response_model=List[ReservaModel])
def get_by_cancha_id(cancha_id: int, db: Session = Depends(get_db)):
    try:
        reservas = repo.get_all_by_cancha_id(db, cancha_id)
        return reservas
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@reservas_router.get("/cancha/{cancha_id}/{dia}", response_model=List[ReservaModel])
def get_by_dia(cancha_id: int, dia: datetime, db: Session = Depends(get_db)):
    try:
        reservas = repo.get_by_dia(db, cancha_id, dia)
        return reservas
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}"
        )


@reservas_router.post(
    "/", response_model=ReservaModel, status_code=status.HTTP_201_CREATED
)
def create(reserva: ReservaModel, db: Session = Depends(get_db)):
    reserva = Reserva(**reserva.model_dump(exclude_unset=True))
    return repo.create(reserva, db)


@reservas_router.patch("/{reserva_id}", response_model=ReservaModel)
def edit(reserva_id: int, datos: ReservaUpdate, db: Session = Depends(get_db)):
    try:
        reserva = Reserva(**datos.model_dump(exclude_unset=True))
        return repo.edit(db, reserva_id, reserva)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}"
        )


@reservas_router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(reserva_id: int, db: Session = Depends(get_db)):
    try:
        return repo.delete(db, reserva_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}"
        )
