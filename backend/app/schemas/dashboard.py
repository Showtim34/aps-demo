"""Schémas Pydantic utilisés par le dashboard."""

from pydantic import BaseModel

from app.models.machine import MachineStatus
from app.schemas.alert import AlertRead
from app.schemas.machine import MachineRead
from app.schemas.measurement import MeasurementRead
from app.schemas.site import SiteRead


class StatusCount(BaseModel):
    """Petit objet de comptage par statut machine."""
    status: MachineStatus
    count: int


class DashboardSummary(BaseModel):
    """Vue agrégée envoyée au dashboard principal."""
    sites_count: int
    machines_count: int
    active_alerts_count: int
    machines_by_status: list[StatusCount]
    recent_measurements: list[MeasurementRead]
    sites: list[SiteRead]
    machines: list[MachineRead]
    active_alerts: list[AlertRead]
