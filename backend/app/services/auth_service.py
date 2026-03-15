"""Service d'authentification.

Un service répond à la question : "quel est le cas d'usage métier ?"

Celui-ci est volontairement petit :

- valider des identifiants
- émettre un token d'accès
"""

from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def authenticate(self, email: str, password: str) -> User:
        """Valide les identifiants et retourne l'utilisateur correspondant."""
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        return user

    def login(self, email: str, password: str) -> str:
        """Cas d'usage public de login qui retourne un JWT."""
        user = self.authenticate(email, password)
        return create_access_token(str(user.id))
