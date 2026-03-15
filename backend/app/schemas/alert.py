"""Schémas Pydantic liés aux alertes."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertLevel


class AlertRead(BaseModel):
    """Représentation d'une alerte en sortie d'API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    level: AlertLevel
    message: str
    is_active: bool
    created_at: datetime
