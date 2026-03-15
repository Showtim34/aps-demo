"""Utilitaires liés au hash de mot de passe et à la gestion des JWT.

Le backend regroupe ces sujets dans un seul fichier pour garder les routers et
les services lisibles :

- hash et vérification des mots de passe
- création de token
- décodage de token
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

# `pwdlib` choisit pour nous un algorithme moderne.
# Cela garde l'exemple simple tout en utilisant une vraie stratégie de hash,
# plutôt que de stocker les mots de passe en clair.
password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare un mot de passe en clair avec son hash stocké."""
    return password_hash.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash un mot de passe avant de l'enregistrer en base."""
    return password_hash.hash(password)


def create_access_token(subject: str) -> str:
    """Crée un JWT signé pour un utilisateur.

    `subject` est l'identifiant utilisateur stocké dans le claim `sub`. La
    date d'expiration est elle aussi embarquée dans le token.
    """

    settings = get_settings()
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    """Décode et vérifie un JWT.

    Si la signature ou l'expiration est invalide, `jwt.decode` lève une
    exception. La couche de dépendances convertit ensuite cela en HTTP 401.
    """

    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
