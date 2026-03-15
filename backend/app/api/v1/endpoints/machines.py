"""Routes HTTP liées aux machines."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import DbSession, get_current_user
from app.models.machine import MachineStatus
from app.models.user import User
from app.schemas.machine import MachineCreate, MachineDetail, MachineRead, MachineUpdate
from app.schemas.measurement import MeasurementRead
from app.services.machine_service import MachineService
from app.services.measurement_service import MeasurementService

router = APIRouter()


@router.get("", response_model=list[MachineRead])
def list_machines(
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
    site_id: int | None = Query(default=None),
    status: MachineStatus | None = Query(default=None),
) -> list[MachineRead]:
    """Lister les machines avec filtres optionnels."""
    machines = MachineService(db).list_machines(site_id=site_id, status=status)
    return [MachineRead.model_validate(machine) for machine in machines]


@router.post("", response_model=MachineRead, status_code=status.HTTP_201_CREATED)
def create_machine(
    payload: MachineCreate,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> MachineRead:
    """Créer une machine."""
    machine = MachineService(db).create_machine(payload)
    return MachineRead.model_validate(machine)


@router.get("/{machine_id}", response_model=MachineDetail)
def get_machine(
    machine_id: int,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> MachineDetail:
    """Lire le détail d'une machine avec son site."""
    machine = MachineService(db).get_machine(machine_id)
    return MachineDetail.model_validate(machine)


@router.patch("/{machine_id}", response_model=MachineRead)
def update_machine(
    machine_id: int,
    payload: MachineUpdate,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> MachineRead:
    """Modifier partiellement une machine existante."""
    machine = MachineService(db).update_machine(machine_id, payload)
    return MachineRead.model_validate(machine)


@router.get("/{machine_id}/measurements", response_model=list[MeasurementRead])
def list_machine_measurements(
    machine_id: int,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[MeasurementRead]:
    """Lister les mesures d'une machine, de la plus récente à la plus ancienne."""
    measurements = MeasurementService(db).list_machine_measurements(machine_id)
    return [MeasurementRead.model_validate(measurement) for measurement in measurements]
