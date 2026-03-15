"""Logique métier exécutée à la réception d'une télémétrie.

C'est un des fichiers les plus intéressants côté domaine, car une seule mesure
entrante déclenche plusieurs effets de bord :

- persister la mesure
- évaluer les seuils
- créer, mettre à jour ou fermer des alertes
- mettre à jour l'état de la machine
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.alert import AlertLevel
from app.models.machine import MachineStatus
from app.repositories.alert_repository import AlertRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.realtime.mqtt import mqtt_runtime
from app.services.dashboard_service import DashboardService
from app.schemas.measurement import MeasurementCreate

logger = get_logger(__name__)


class MeasurementService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.measurements = MeasurementRepository(db)
        self.machines = MachineRepository(db)
        self.alerts = AlertRepository(db)

    def list_machine_measurements(self, machine_id: int):
        """Cas d'usage en lecture pour la page de détail d'une machine."""
        machine = self.machines.get_by_id(machine_id)
        if machine is None:
            raise NotFoundError("Machine not found")
        return self.measurements.list_for_machine(machine_id)

    def create_measurement(
        self,
        payload: MeasurementCreate,
        *,
        publish_event: bool = True,
    ):
        """Persiste la télémétrie et applique les règles métier.

        Cette méthode regroupe volontairement tout le workflow dans une seule
        transaction :

        1. valider l'existence de la machine
        2. enregistrer la mesure
        3. évaluer les seuils
        4. mettre à jour les alertes
        5. mettre à jour l'état de la machine
        6. tout valider avec un seul commit
        """

        machine = self.machines.get_by_id(payload.machine_id)
        if machine is None:
            raise NotFoundError("Machine not found")

        measurement = self.measurements.create(
            machine_id=payload.machine_id,
            temperature=payload.temperature,
            vibration=payload.vibration,
            power=payload.power,
            recorded_at=payload.recorded_at or datetime.now(timezone.utc),
        )
        logger.info("Measurement created for machine %s", machine.code)

        evaluation = self._evaluate_thresholds(
            temperature=payload.temperature,
            vibration=payload.vibration,
            power=payload.power,
        )

        if evaluation is None:
            # Une mesure saine ferme les alertes ouvertes et remet la machine
            # en fonctionnement.
            self.alerts.deactivate_for_machine(machine.id)
            machine.status = MachineStatus.RUNNING
        else:
            # Lorsqu'un seuil est dépassé, la machine passe à l'état `alert`.
            machine.status = MachineStatus.ALERT
            active_alerts = self.alerts.list_active_for_machine(machine.id)
            if active_alerts:
                # On met à jour une alerte active existante au lieu d'en créer
                # une nouvelle à chaque valeur critique reçue.
                for alert in active_alerts:
                    alert.level = evaluation["level"]
                    alert.message = evaluation["message"]
                    self.alerts.save(alert)
            else:
                self.alerts.create(
                    machine_id=machine.id,
                    level=evaluation["level"],
                    message=evaluation["message"],
                )
            logger.warning(
                "Alert triggered for machine %s with level %s",
                machine.code,
                evaluation["level"],
            )

        self.machines.save(machine)
        self.db.commit()
        self.db.refresh(measurement)
        if publish_event:
            summary = DashboardService(self.db).get_summary().model_dump(mode="json")
            mqtt_runtime.publish_dashboard_event(
                kind="alert" if evaluation is not None else "measurement",
                machine_id=measurement.machine_id,
                reason="measurement_created_via_api",
                summary=summary,
            )
        return measurement

    @staticmethod
    def _evaluate_thresholds(
        *, temperature: float, vibration: float, power: float
    ) -> dict[str, AlertLevel | str] | None:
        """Traduit une télémétrie brute en décision d'alerte.

        Retourner `None` signifie que la mesure est saine.
        Retourner un dictionnaire fournit le niveau d'alerte et le message à
        persister.
        """

        if temperature > 95 or vibration > 8 or power > 98:
            return {
                "level": AlertLevel.CRITICAL,
                "message": "Critical threshold exceeded on machine telemetry.",
            }
        if temperature > 80 or vibration > 6 or power > 90:
            return {
                "level": AlertLevel.WARNING,
                "message": "Warning threshold exceeded on machine telemetry.",
            }
        return None
