from typing import List
from sqlalchemy.orm import Session
from domain.model.reservas import Reserva
from domain.exceptions.NotFound import NotFoundError
from domain.model.cancha import Cancha
from sqlalchemy import text
from datetime import timedelta, datetime


class ReservasRepo:
    """
    Clase para manejar las operaciones CRUD en la tabla reservas
    """
    # Metodos CRUD
    def get_all(self, db: Session) -> List[Reserva]:
        return db.query(Reserva).all()

    def get_by_id(self, db: Session, reserva_id: int) -> Reserva:
        result = db.get(Reserva, reserva_id)
        if result is None:
            raise NotFoundError(f"Reserva {reserva_id} no encontrada")
        return result

    def get_all_by_cancha_id(self, db: Session, cancha_id: int) -> List[Reserva]:
        cancha = db.get(Cancha, cancha_id)
        if cancha is None:
            raise NotFoundError(f"Cancha ID:{cancha_id} no encontrada.")
        return db.query(Reserva).filter(Reserva.cancha_id == cancha_id).all()

    def get_by_dia(self, db: Session, cancha_id: int, dia: datetime) -> List[Reserva]:
        cancha = db.get(Cancha, cancha_id)
        if cancha is None:
            raise NotFoundError(f"Cancha ID:{cancha_id} no encontrada.")
        inicio_dia = dia.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        return (
            db.query(Reserva)
            .filter(
                Reserva.cancha_id == cancha_id,
                Reserva.dia_hora >= inicio_dia,
                Reserva.dia_hora < fin_dia,
            )
            .all()
        )

    def create(self, reserva: Reserva, db: Session) -> Reserva:
        if self.verificar_conflictos(reserva, db):
            raise Exception(
                "La reserva coincide con otra existente en la misma cancha."
            )
        db.add(reserva)
        db.commit()
        return reserva

    def edit(self, db: Session, id: int, datos: dict) -> Reserva:
        reserva = self.get_by_id(db, id)
        for key, value in datos.items():
            setattr(reserva, key, value)
        if self.verificar_conflictos(reserva, db, id):
            raise Exception(
                "La reserva modificada coincide con otra existente en la misma cancha."
            )
        db.commit()
        db.refresh(reserva)
        return reserva

    def delete(self, db: Session, reserva_id: int) -> None:
        reserva = self.get_by_id(db, reserva_id)
        db.delete(reserva)
        db.commit()

    # Otros metodos
    def reservas_count(self, db: Session) -> int:
        return db.query(Reserva).count()

    def verificar_conflictos(
        self, reserva: Reserva, db: Session, reserva_id: int = None
    ):
        # Obtener la cancha para verificar que exista
        # cancha = db.query(Cancha).filter(Cancha.id == reserva.cancha_id).first()
        cancha = db.get(Cancha, reserva.cancha_id)
        if cancha is None:
            raise NotFoundError(f"Cancha ID:{reserva.cancha_id} no encontrada.")
        try:
            # Verificar conflictos de horarios en las reservas existentes
            conflictos = (
                db.query(Reserva)
                .filter(
                    Reserva.cancha_id == reserva.cancha_id,  # Misma cancha
                    Reserva.id != reserva_id,  # Ignorar la reserva actual
                    # Comparar las fechas y duraciones
                    (
                        reserva.dia_hora
                        < (
                            Reserva.dia_hora
                            + text(f"INTERVAL '{reserva.duracion} hours'")
                        )
                    ),
                    (
                        (reserva.dia_hora + timedelta(hours=reserva.duracion))
                        > Reserva.dia_hora
                    ),
                )
                .first()
            )
            return conflictos
            # region OLD
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
            # endregion
        except Exception as e:
            raise Exception(f"Error: {e}")
