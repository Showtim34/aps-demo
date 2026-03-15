"""Schémas Pydantic liés aux mesures de capteurs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeasurementCreate(BaseModel):
    """Payload de création d'une mesure.

    Les bornes `Field(...)` montrent comment Pydantic peut aussi faire de la
    validation métier simple avant d'entrer dans le service.
    """
    machine_id: int
    temperature: float = Field(ge=0, le=150)
    vibration: float = Field(ge=0, le=20)
    power: float = Field(ge=0, le=120)
    recorded_at: datetime | None = None


class MeasurementRead(BaseModel):
    """Représentation d'une mesure côté API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    temperature: float
    vibration: float
    power: float
    recorded_at: datetime
