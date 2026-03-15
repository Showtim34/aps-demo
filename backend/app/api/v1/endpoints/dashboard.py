"""Routes du dashboard."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> DashboardSummary:
    """Retourner toutes les données agrégées utiles au dashboard."""
    return DashboardService(db).get_summary()
