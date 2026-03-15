"""Service qui assemble les données du dashboard depuis plusieurs repositories."""

from collections import Counter

from sqlalchemy.orm import Session

from app.models.machine import MachineStatus
from app.repositories.alert_repository import AlertRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.dashboard import DashboardSummary, StatusCount


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.sites = SiteRepository(db)
        self.machines = MachineRepository(db)
        self.measurements = MeasurementRepository(db)
        self.alerts = AlertRepository(db)

    def get_summary(self) -> DashboardSummary:
        """Agrège les compteurs et listes nécessaires à la page dashboard."""
        sites = self.sites.list_all()
        machines = self.machines.list_all()
        active_alerts = self.alerts.list_all(active_only=True)
        recent_measurements = self.measurements.recent(limit=12)

        # `Counter` est un outil Python simple pour compter par clé.
        counter = Counter(machine.status for machine in machines)
        by_status = [
            StatusCount(status=status, count=counter.get(status, 0))
            for status in MachineStatus
        ]

        return DashboardSummary(
            sites_count=len(sites),
            machines_count=len(machines),
            active_alerts_count=len(active_alerts),
            machines_by_status=by_status,
            recent_measurements=recent_measurements,
            sites=sites,
            machines=machines,
            active_alerts=active_alerts,
        )
