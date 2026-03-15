"""Routes HTTP liées aux alertes.

Les routers FastAPI doivent rester minces :

- lire les paramètres HTTP
- appeler le service métier
- renvoyer des schémas de sortie
"""

# `Annotated` permet d'associer un type Python à une dépendance FastAPI.
from typing import Annotated

# `DbSession` injecte une session SQLAlchemy par requête.
# `get_current_user` force ici l'authentification avant d'entrer dans la route.
from app.api.deps import DbSession, get_current_user

# Modèle ORM utilisateur, utilisé seulement pour typer la dépendance d'auth.
from app.models.user import User
from app.models.alert import AlertLevel

# Schéma Pydantic de sortie pour exposer une alerte côté API.
from app.schemas.alert import AlertRead

# Service applicatif qui porte le cas d'usage métier de lecture des alertes.
from app.services.alert_service import AlertService
# `APIRouter` crée un groupe de routes.
# `Depends` déclare une dépendance injectée automatiquement.
# `Query` décrit un paramètre de query string avec ses métadonnées.
from fastapi import APIRouter, Depends, Query

# Crée un router vide ; son préfixe est défini plus haut dans l'assemblage API.
router = APIRouter()


# Déclare une route HTTP GET sur le chemin du router courant.
# `response_model=list[AlertRead]` indique à FastAPI la forme de la réponse.
@router.get("", response_model=list[AlertRead])
def list_alerts(
    # Session de base injectée automatiquement pour parler à la DB.
    db: DbSession,
    # Dépendance d'authentification :
    # FastAPI doit résoudre l'utilisateur courant avant d'exécuter la route.
    # Le `_` signifie qu'on n'utilise pas la variable ensuite, mais qu'on veut
    # quand même imposer le contrôle d'accès.
    _: Annotated[User, Depends(get_current_user)],
    # Paramètre de query string `?active_only=true|false`.
    # Par défaut, l'endpoint ne retourne que les alertes actives.
    active_only: bool = Query(default=True),
    # Limite optionnelle sur le nombre d'alertes retournées.
    limit: int | None = Query(default=None, ge=1),
    # Filtre optionnel sur le niveau d'alerte (`warning` ou `critical`).
    level: AlertLevel | None = Query(default=None),
) -> list[AlertRead]:
    """Lister les alertes, actives uniquement par défaut."""
    # Appelle le service métier avec le filtre demandé par le client HTTP.
    alerts = AlertService(db).list_alerts(
        active_only=active_only, limit=limit, level=level
    )
    # Transforme les objets ORM en schémas de sortie Pydantic.
    # En Symfony, pense à une normalisation/sérialisation de DTO de réponse.
    return [AlertRead.model_validate(alert) for alert in alerts]
