"""Service métier pour les sites."""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.site_repository import SiteRepository
from app.schemas.site import SiteCreate


class SiteService:
    def __init__(self, db: Session) -> None:
        self.sites = SiteRepository(db)

    def list_sites(self):
        """Retourner tous les sites."""
        return self.sites.list_all()

    def get_site(self, site_id: int):
        """Retourner un site ou lever une erreur métier."""
        site = self.sites.get_by_id(site_id)
        if site is None:
            raise NotFoundError("Site not found")
        return site

    def create_site(self, payload: SiteCreate):
        """Créer un site à partir du schéma d'entrée."""
        return self.sites.create(
            name=payload.name,
            city=payload.city,
            country=payload.country,
        )
