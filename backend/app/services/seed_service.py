"""Service de seed utilisé pour créer des données de démonstration cohérentes.

Le seed est volontairement implémenté en Python plutôt qu'en SQL brut pour
qu'on puisse suivre les mêmes repositories et modèles que dans l'application
réelle.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.alert import AlertLevel
from app.models.machine import MachineStatus
from app.repositories.alert_repository import AlertRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class SeedService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.users = UserRepository(db)
        self.sites = SiteRepository(db)
        self.machines = MachineRepository(db)
        self.measurements = MeasurementRepository(db)
        self.alerts = AlertRepository(db)

    def run(self) -> dict[str, str]:
        """Point d'entrée principal du seed utilisé par l'endpoint API."""
        logger.info("Launching demo seed")
        self.ensure_admin_user()
        sites = self._seed_sites()
        machines = self._seed_machines(sites)
        self._seed_measurements(machines)
        self.db.commit()
        return {
            "message": "Demo data ready",
            "admin_email": self.settings.first_admin_email,
            "admin_password": self.settings.first_admin_password,
        }

    def ensure_admin_user(self) -> None:
        """Crée le compte admin s'il n'existe pas déjà."""
        if self.users.get_by_email(self.settings.first_admin_email):
            return
        self.users.create(
            email=self.settings.first_admin_email,
            hashed_password=hash_password(self.settings.first_admin_password),
            full_name="Demo Administrator",
        )

    def _seed_sites(self):
        """Crée un petit ensemble de sites industriels."""
        site_specs = [
            ("Lyon Foundry", "Lyon", "France"),
            ("Hamburg Assembly", "Hamburg", "Germany"),
            ("Bilbao Energy Hub", "Bilbao", "Spain"),
        ]
        sites = []
        existing = {site.name: site for site in self.sites.list_all()}
        for name, city, country in site_specs:
            site = existing.get(name) or self.sites.create(name=name, city=city, country=country)
            sites.append(site)
        return sites

    def _seed_machines(self, sites):
        """Crée des machines de démonstration rattachées aux sites seedés."""
        machine_specs = [
            (sites[0].id, "LYN-CNC-01", "CNC Press 01", "press", MachineStatus.RUNNING),
            (sites[0].id, "LYN-PMP-02", "Hydraulic Pump 02", "pump", MachineStatus.RUNNING),
            (sites[1].id, "HAM-CONV-01", "Conveyor 01", "conveyor", MachineStatus.IDLE),
            (sites[1].id, "HAM-RBT-04", "Robot Arm 04", "robot", MachineStatus.MAINTENANCE),
            (sites[2].id, "BIL-GEN-01", "Generator 01", "generator", MachineStatus.ALERT),
            (sites[2].id, "BIL-COOL-03", "Cooling Unit 03", "cooling", MachineStatus.RUNNING),
        ]
        machines = []
        for site_id, code, name, machine_type, status in machine_specs:
            machine = self.machines.get_by_code(code)
            if machine is None:
                machine = self.machines.create(
                    site_id=site_id,
                    code=code,
                    name=name,
                    machine_type=machine_type,
                    status=status,
                )
            machines.append(machine)
        return machines

    def _seed_measurements(self, machines) -> None:
        """Crée de la télémétrie d'exemple et quelques alertes.

        Les valeurs générées sont assez déterministes pour que la démo reste
        facile à comprendre. Une machine est volontairement poussée dans un
        état critique.
        """
        for index, machine in enumerate(machines):
            if self.measurements.list_for_machine(machine.id, limit=1):
                continue
            for offset in range(4):
                recorded_at = datetime.now(timezone.utc) - timedelta(hours=4 - offset)
                temperature = 62 + index * 4 + offset
                vibration = 2.1 + (index % 3) + (offset * 0.2)
                power = 55 + index * 5 + offset * 2
                if machine.code == "BIL-GEN-01" and offset >= 2:
                    temperature = 97
                    vibration = 8.5
                    power = 99
                    machine.status = MachineStatus.ALERT
                self.measurements.create(
                    machine_id=machine.id,
                    temperature=temperature,
                    vibration=vibration,
                    power=power,
                    recorded_at=recorded_at,
                )
                if temperature > 95 or vibration > 8 or power > 98:
                    if not self.alerts.list_active_for_machine(machine.id):
                        self.alerts.create(
                            machine_id=machine.id,
                            level=AlertLevel.CRITICAL,
                            message="Critical threshold exceeded on machine telemetry.",
                        )
                elif temperature > 80 or vibration > 6 or power > 90:
                    if not self.alerts.list_active_for_machine(machine.id):
                        self.alerts.create(
                            machine_id=machine.id,
                            level=AlertLevel.WARNING,
                            message="Warning threshold exceeded on machine telemetry.",
                        )
