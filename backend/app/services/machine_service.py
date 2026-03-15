"""Logique métier autour des machines."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.machine_repository import MachineRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.machine import MachineCreate, MachineUpdate


class MachineService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.machines = MachineRepository(db)
        self.sites = SiteRepository(db)

    def list_machines(self, *, site_id=None, status=None):
        return self.machines.list_all(site_id=site_id, status=status)

    def get_machine(self, machine_id: int):
        machine = self.machines.get_by_id(machine_id)
        if machine is None:
            raise NotFoundError("Machine not found")
        return machine

    def create_machine(self, payload: MachineCreate):
        """Crée une machine après validation du site et de l'unicité du code."""
        if self.sites.get_by_id(payload.site_id) is None:
            raise NotFoundError("Site not found")
        if self.machines.get_by_code(payload.code) is not None:
            raise ConflictError("Machine code already exists")
        machine = self.machines.create(
            site_id=payload.site_id,
            code=payload.code,
            name=payload.name,
            machine_type=payload.machine_type,
            status=payload.status,
        )
        self.db.commit()
        self.db.refresh(machine)
        return machine

    def update_machine(self, machine_id: int, payload: MachineUpdate):
        """Met à jour les champs modifiables d'une machine existante."""
        machine = self.get_machine(machine_id)
        if payload.name is not None:
            machine.name = payload.name
        if payload.machine_type is not None:
            machine.machine_type = payload.machine_type
        if payload.status is not None:
            machine.status = payload.status
        self.machines.save(machine)
        self.db.commit()
        self.db.refresh(machine)
        return machine
