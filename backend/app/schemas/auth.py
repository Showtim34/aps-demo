"""Schémas Pydantic liés à l'authentification et au seed."""

from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    """Payload attendu pour le login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Réponse renvoyée après authentification réussie."""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Petit schéma générique pour des réponses textuelles simples."""
    message: str


class SeedResponse(BaseModel):
    """Réponse renvoyée par le endpoint de seed."""
    model_config = ConfigDict(from_attributes=True)

    message: str
    admin_email: str
    admin_password: str
