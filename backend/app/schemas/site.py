"""Schémas Pydantic liés aux sites."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SiteCreate(BaseModel):
    """Payload de création d'un site."""
    name: str
    city: str
    country: str


class SiteRead(BaseModel):
    """Représentation d'un site en sortie d'API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    country: str
    created_at: datetime
