"""Repository dédié à la persistance des utilisateurs.

Un repository répond à la question : "comment parle-t-on à la base pour cette
entité ?"

Il ne doit pas contenir de logique HTTP et doit embarquer très peu de logique
métier.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Retourne un utilisateur ou `None`."""
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def create(self, *, email: str, hashed_password: str, full_name: str) -> User:
        """Crée un utilisateur et flush pour rendre son `id` disponible tout de suite."""
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        self.db.add(user)
        self.db.flush()
        return user
