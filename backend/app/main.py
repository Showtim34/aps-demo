"""Point d'entrée de l'application FastAPI."""

# Fournit un gestionnaire de contexte asynchrone pour brancher du code de
# démarrage et d'arrêt autour de l'application.
from contextlib import asynccontextmanager

# `FastAPI` instancie l'application web.
# `Request` représente la requête HTTP courante.
from fastapi import FastAPI, Request

# Middleware CORS pour autoriser le frontend à appeler l'API depuis un autre
# domaine/port.
from fastapi.middleware.cors import CORSMiddleware

# Réponse JSON prête à l'emploi, pratique pour les handlers d'erreur.
from fastapi.responses import JSONResponse

# Routeur principal de l'API v1, qui regroupe les endpoints métiers.
from app.api.v1.api import api_router

# Charge la configuration typée depuis l'environnement.
from app.core.config import get_settings

# Exception métier de base que l'on convertira plus bas en réponse HTTP.
from app.core.exceptions import AppError

# Outils internes pour initialiser et récupérer les logs.
from app.core.logging import configure_logging, get_logger

# Fabrique de session SQLAlchemy pour ouvrir une connexion ORM.
from app.db.session import SessionLocal

# Runtime MQTT qui gère l'abonnement et la publication d'événements temps réel.
from app.realtime.mqtt import mqtt_runtime

# Service de seed, utilisé ici pour garantir l'existence du premier admin.
from app.services.seed_service import SeedService

# Construit l'objet de configuration une seule fois au chargement du module.
settings = get_settings()
# Initialise la configuration du logging en fonction du mode debug.
configure_logging(settings.app_debug)
# Récupère un logger nommé avec le chemin du module courant.
logger = get_logger(__name__)


# Indique à FastAPI que cette fonction décrit le cycle de vie de l'application.
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Exécute le code de démarrage et d'arrêt autour du cycle de vie applicatif."""
    # Écrit dans les logs que l'application démarre avec son nom et son environnement.
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    # Lance la couche MQTT au démarrage pour écouter la télémétrie.
    mqtt_runtime.start()
    # Ouvre une session SQLAlchemy pour exécuter l'initialisation en base.
    db = SessionLocal()
    try:
        # Garde le premier admin disponible même avant le lancement explicite du seed.
        SeedService(db).ensure_admin_user()
        # Valide la transaction si la création/lecture de l'admin s'est bien passée.
        db.commit()
    except Exception as exc:  # noqa: BLE001
        # Si l'initialisation échoue, on loggue un warning mais on ne bloque pas le boot.
        logger.warning("Admin bootstrap skipped: %s", exc)
    finally:
        # Ferme toujours la session pour rendre la connexion au pool SQLAlchemy.
        db.close()
    # Rend la main à FastAPI : tout ce qui est avant `yield` correspond au startup.
    yield
    # Tout ce qui est après `yield` s'exécute à l'arrêt de l'application.
    # On coupe donc la couche MQTT proprement.
    mqtt_runtime.stop()
    # Trace l'arrêt de l'application dans les logs.
    logger.info("Stopping %s", settings.app_name)


# Crée l'application FastAPI principale.
app = FastAPI(
    # Nom affiché dans la documentation OpenAPI/Swagger.
    title=settings.app_name,
    # Active les aides de debug si l'environnement le demande.
    debug=settings.app_debug,
    # Branche notre hook de démarrage/arrêt défini ci-dessus.
    lifespan=lifespan,
)

# Ajoute le middleware CORS dans la pile HTTP.
app.add_middleware(
    # Type de middleware ajouté.
    CORSMiddleware,
    # Liste des origines autorisées à appeler l'API.
    allow_origins=settings.cors_origins,
    # Autorise l'envoi de credentials (cookies, headers d'auth, etc.).
    allow_credentials=True,
    # Autorise toutes les méthodes HTTP.
    allow_methods=["*"],
    # Autorise tous les headers HTTP.
    allow_headers=["*"],
)


# Enregistre un handler global pour toutes les erreurs métier de type `AppError`.
@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Traduit les erreurs métier en réponses HTTP JSON cohérentes."""
    # Retourne une réponse JSON uniforme avec le code HTTP porté par l'exception.
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Déclare une route HTTP GET très simple sur `/health`.
@app.get("/health")
def health() -> dict[str, str]:
    """Petit endpoint utilisé par les humains, les conteneurs ou un reverse proxy."""
    # Renvoie un payload minimal pour indiquer que l'API répond bien.
    return {"status": "ok", "service": "api"}


# Déclare une route HTTP GET très simple sur `/health`.
@app.get("/health/details")
def health_details() -> dict[str, str | bool]:
    """Retourne un état de santé détaillé de l'API."""

    # Renvoie un payload minimal pour indiquer que l'API répond bien.
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.app_env,
        "version": settings.app_version,
        "debug": settings.app_debug,
        "uptime_hint": "startup-managed",
    }


# Déclare une route HTTP GET très simple sur `/health`.
@app.get("/health/version")
def health_version() -> dict[str, str]:
    """Retourne la version l'API."""

    # Renvoie un payload minimal pour indiquer que l'API répond bien.
    return {
        "name": settings.app_name,
        "version": settings.app_version,
    }


# Monte tout le routeur API sous le préfixe configuré, par exemple `/api/v1`.
app.include_router(api_router, prefix=settings.api_v1_prefix)
