"""Schémas Pydantic liés aux machines."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.machine import MachineStatus
from app.schemas.site import SiteRead


class MachineCreate(BaseModel):
    """Payload de création d'une machine."""
    site_id: int
    code: str
    name: str
    machine_type: str
    status: MachineStatus = MachineStatus.IDLE


class MachineUpdate(BaseModel):
    """Payload de mise à jour partielle d'une machine."""
    name: str | None = None
    machine_type: str | None = None
    status: MachineStatus | None = None


class MachineRead(BaseModel):
    """Représentation standard d'une machine."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    code: str
    name: str
    machine_type: str
    status: MachineStatus
    created_at: datetime


class MachineDetail(MachineRead):
    """Détail machine enrichi avec les données du site."""
    site: SiteRead
