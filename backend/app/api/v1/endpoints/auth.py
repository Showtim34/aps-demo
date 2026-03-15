"""Routes d'authentification."""

from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    """Authentifier un utilisateur et retourner un JWT."""
    token = AuthService(db).login(payload.email, payload.password)
    return TokenResponse(access_token=token)
