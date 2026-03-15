"""Dépendances FastAPI partagées par plusieurs routers.

Les dépendances sont un des concepts clés à comprendre dans FastAPI :

- elles centralisent la logique répétitive
- elles peuvent injecter des objets dans les fonctions de route
- elles sont très adaptées à l'auth, aux sessions DB, aux permissions, etc.
"""

from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Cet alias garde les signatures de routes courtes et lisibles.
DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]):
    """Résout l'utilisateur authentifié à partir du bearer token.

    Flux :

    1. lire `Authorization: Bearer ...`
    2. décoder et vérifier le JWT
    3. extraire l'identifiant utilisateur depuis le claim `sub`
    4. charger l'utilisateur depuis la base
    """

    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid authentication token") from exc

    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("Invalid authentication token")

    user = UserRepository(db).get_by_id(int(subject))
    if user is None:
        raise UnauthorizedError("User not found")
    return user
