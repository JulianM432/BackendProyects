from domain.model.cancha import Cancha
from domain.exceptions.NotFound import NotFoundError
from typing import List
from sqlalchemy.orm import Session


class CanchaRepo:
    """
    Clase para manejar las operaciones CRUD en la tabla canchas
    """
    # Metodos CRUD
    def get_all(self, db: Session) -> List[Cancha]:
        return db.query(Cancha).all()

    def get_by_id(self, db: Session, cancha_id: int) -> Cancha:
        result = db.get(Cancha, cancha_id)
        if result is None:
            raise NotFoundError(f"Cancha {cancha_id} no encontrada")
        return result

    def create(self, cancha: Cancha, db: Session) -> Cancha:
        db.add(cancha)
        db.commit()
        return cancha

    def edit(self, db: Session, id: int, datos: dict) -> Cancha:
        cancha = self.get_by_id(db, id)
        for key, value in datos.items():
            setattr(cancha, key, value)
        db.commit()
        return cancha

    def delete(self, db: Session, cancha_id: int) -> None:
        cancha = self.get_by_id(db, cancha_id)
        db.delete(cancha)
        db.commit()

    # Otros metodos
    def canchas_count(self, db: Session) -> int:
        return db.query(Cancha).count()
