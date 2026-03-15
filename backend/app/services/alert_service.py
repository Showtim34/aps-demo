"""Service applicatif pour les alertes."""

from app.models.alert import Alert, AlertLevel
from app.repositories.alert_repository import AlertRepository
from sqlalchemy.orm import Session


class AlertService:
    def __init__(self, db: Session) -> None:
        self.alerts = AlertRepository(db)

    def list_alerts(
        self,
        active_only: bool,
        limit: int | None = None,
        level: AlertLevel | None = None,
    ) -> list[Alert]:
        """Lister les alertes selon le filtre demandé par l'API."""
        return self.alerts.list_all(active_only=active_only, limit=limit, level=level)
