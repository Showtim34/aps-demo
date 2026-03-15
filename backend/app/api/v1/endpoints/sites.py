"""Routes HTTP liées aux sites."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.site import SiteCreate, SiteRead
from app.services.site_service import SiteService

router = APIRouter()


@router.get("", response_model=list[SiteRead])
def list_sites(
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[SiteRead]:
    """Lister tous les sites."""
    return [SiteRead.model_validate(site) for site in SiteService(db).list_sites()]


@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
def create_site(
    payload: SiteCreate,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> SiteRead:
    """Créer un nouveau site."""
    site = SiteService(db).create_site(payload)
    db.commit()
    db.refresh(site)
    return SiteRead.model_validate(site)


@router.get("/{site_id}", response_model=SiteRead)
def get_site(
    site_id: int,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> SiteRead:
    """Lire un site par son identifiant."""
    return SiteRead.model_validate(SiteService(db).get_site(site_id))
