"""Moteur SQLAlchemy et fabrique de sessions.

Si tu viens de PHP/Symfony, tu peux voir ce fichier comme l'endroit où l'on
configure la fabrique de connexion à la base.

Deux concepts importants apparaissent ici :

- `engine` : l'objet bas niveau qui sait parler à la base de données
- `SessionLocal` : une fabrique qui crée des unités de travail utilisées par
  les repositories et les services
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Le moteur est créé une seule fois pour tout le processus de l'application.
engine = create_engine(settings.database_url, future=True)

# `sessionmaker` est une fabrique. Appeler `SessionLocal()` crée une Session
# SQLAlchemy liée à la requête ou à la tâche en cours.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI qui fournit une session DB par requête.

    Le pattern `yield` est important dans FastAPI :

    - le code avant `yield` prépare la dépendance
    - le code après `yield` s'exécute pendant le nettoyage
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        # On ferme toujours la session pour rendre la connexion au pool.
        db.close()
