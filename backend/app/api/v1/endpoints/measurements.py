"""Routes HTTP liées aux mesures."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.measurement import MeasurementCreate, MeasurementRead
from app.services.measurement_service import MeasurementService

router = APIRouter()


@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(
    payload: MeasurementCreate,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> MeasurementRead:
    """Créer une mesure via HTTP.

    Cette route et le consommateur MQTT réutilisent le même service métier.
    """
    measurement = MeasurementService(db).create_measurement(payload)
    return MeasurementRead.model_validate(measurement)
