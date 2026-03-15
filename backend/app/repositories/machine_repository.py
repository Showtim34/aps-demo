"""Repository pour les requêtes et la persistance des machines."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.machine import Machine, MachineStatus


class MachineRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(
        self, *, site_id: int | None = None, status: MachineStatus | None = None
    ) -> list[Machine]:
        # `joinedload(Machine.site)` évite une requête supplémentaire quand le
        # service ou le schéma a besoin des informations du site.
        query = select(Machine).options(joinedload(Machine.site)).order_by(Machine.code)
        if site_id is not None:
            query = query.where(Machine.site_id == site_id)
        if status is not None:
            query = query.where(Machine.status == status)
        return list(self.db.scalars(query))

    def get_by_id(self, machine_id: int) -> Machine | None:
        query = select(Machine).options(joinedload(Machine.site)).where(Machine.id == machine_id)
        return self.db.scalar(query)

    def get_by_code(self, code: str) -> Machine | None:
        return self.db.scalar(select(Machine).where(Machine.code == code))

    def create(
        self,
        *,
        site_id: int,
        code: str,
        name: str,
        machine_type: str,
        status: MachineStatus,
    ) -> Machine:
        machine = Machine(
            site_id=site_id,
            code=code,
            name=name,
            machine_type=machine_type,
            status=status,
        )
        self.db.add(machine)
        self.db.flush()
        return machine

    def save(self, machine: Machine) -> Machine:
        """Réattache puis flush une machine déjà chargée après modification."""
        self.db.add(machine)
        self.db.flush()
        return machine
