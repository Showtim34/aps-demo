"""Routes utilitaires pour la démonstration."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.auth import SeedResponse
from app.services.seed_service import SeedService

router = APIRouter()


@router.post("/seed", response_model=SeedResponse)
def seed_demo_data(
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> SeedResponse:
    """Injecter les données de démonstration."""
    result = SeedService(db).run()
    return SeedResponse(**result)
