"""Repository pour les sites."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.site import Site


class SiteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Site]:
        """Lister tous les sites triés par nom."""
        return list(self.db.scalars(select(Site).order_by(Site.name)))

    def get_by_id(self, site_id: int) -> Site | None:
        return self.db.get(Site, site_id)

    def create(self, *, name: str, city: str, country: str) -> Site:
        """Créer un site et flusher pour obtenir son identifiant."""
        site = Site(name=name, city=city, country=country)
        self.db.add(site)
        self.db.flush()
        return site
