"""Paramètres applicatifs chargés depuis les variables d'environnement.

Ce fichier est une bonne porte d'entrée quand on découvre un backend Python :

- `BaseSettings` de `pydantic-settings` joue un rôle proche d'un objet de
  configuration construit à partir d'un `.env`
- chaque attribut devient un paramètre typé
- `get_settings()` est mis en cache pour éviter de reconstruire la config à
  chaque import
"""

from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Objet centralisé de configuration.

    Dans les projets FastAPI, un pattern fréquent est :

    1. définir une seule classe de configuration typée
    2. laisser Pydantic lire automatiquement les variables d'environnement
    3. injecter ou importer cet objet partout où l'application en a besoin
    """

    # `model_config` indique à pydantic-settings où charger les valeurs.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "APS Lab Monitor"
    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "1"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://apslab:apslab@db:5432/apslab"
    first_admin_email: str = "admin@example.com"
    first_admin_password: str = "admin123"
    cors_origins: list[str] = ["http://localhost:3000"]
    mqtt_enabled: bool = True
    mqtt_host: str = "mosquitto"
    mqtt_port: int = 1883
    mqtt_ws_url: str = "ws://localhost:9001"
    mqtt_telemetry_topic: str = "aps/telemetry/measurements"
    mqtt_events_topic_prefix: str = "aps/events"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        """Propriété pratique utilisée quand le comportement dépend de l'environnement."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Retourne une unique instance de configuration mise en cache.

    `@lru_cache` est une façon légère d'implémenter un pattern proche du
    singleton en Python, sans ajouter de complexité framework.
    """

    return Settings()
