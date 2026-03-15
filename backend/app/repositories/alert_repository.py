"""Repository pour la persistance des alertes."""

from app.models.alert import Alert, AlertLevel
from sqlalchemy import select, update
from sqlalchemy.orm import Session


class AlertRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(
        self,
        active_only: bool,
        limit: int | None = None,
        level: AlertLevel | None = None,
    ) -> list[Alert]:
        query = select(Alert).order_by(Alert.created_at.desc())
        if active_only:
            query = query.where(Alert.is_active.is_(True))

        if level is not None:
            query = query.where(Alert.level == level)

        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query))

    def list_active_for_machine(self, machine_id: int) -> list[Alert]:
        query = select(Alert).where(
            Alert.machine_id == machine_id, Alert.is_active.is_(True)
        )
        return list(self.db.scalars(query))

    def create(self, *, machine_id: int, level: AlertLevel, message: str) -> Alert:
        alert = Alert(
            machine_id=machine_id, level=level, message=message, is_active=True
        )
        self.db.add(alert)
        self.db.flush()
        return alert

    def deactivate_for_machine(self, machine_id: int) -> None:
        """Ferme toutes les alertes actives d'une machine en un seul update SQL."""
        self.db.execute(
            update(Alert)
            .where(Alert.machine_id == machine_id, Alert.is_active.is_(True))
            .values(is_active=False)
        )

    def save(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.flush()
        return alert
