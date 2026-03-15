"""Repository pour les mesures de télémétrie."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import Measurement


class MeasurementRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        machine_id: int,
        temperature: float,
        vibration: float,
        power: float,
        recorded_at: datetime,
    ) -> Measurement:
        measurement = Measurement(
            machine_id=machine_id,
            temperature=temperature,
            vibration=vibration,
            power=power,
            recorded_at=recorded_at,
        )
        self.db.add(measurement)
        self.db.flush()
        return measurement

    def list_for_machine(self, machine_id: int, limit: int = 50) -> list[Measurement]:
        """Retourne d'abord les mesures les plus récentes."""
        query = (
            select(Measurement)
            .where(Measurement.machine_id == machine_id)
            .order_by(Measurement.recorded_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def recent(self, limit: int = 10) -> list[Measurement]:
        """Retourne les dernières mesures toutes machines confondues."""
        query = select(Measurement).order_by(Measurement.recorded_at.desc()).limit(limit)
        return list(self.db.scalars(query))
