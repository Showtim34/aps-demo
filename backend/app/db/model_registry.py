"""Importe tous les modèles ORM pour que SQLAlchemy connaisse chaque table.

Ce fichier existe surtout pour Alembic et les tests :

- Alembic a besoin que tous les modèles soient importés avant d'inspecter la
  metadata
- les tests ont le même besoin avant d'appeler `Base.metadata.create_all()`

Le garder séparé évite les imports circulaires dans `db/base.py`.
"""

from app.models.alert import Alert  # noqa: F401
from app.models.machine import Machine  # noqa: F401
from app.models.measurement import Measurement  # noqa: F401
from app.models.site import Site  # noqa: F401
from app.models.user import User  # noqa: F401
