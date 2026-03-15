"""Point central pour nommer les topics MQTT.

Garder les noms de topics dans un seul fichier évite de disperser des chaînes
en dur dans le projet et rend le contrat MQTT plus lisible.
"""

from app.core.config import get_settings


def telemetry_topic() -> str:
    """Topic utilisé par les producteurs qui envoient les mesures brutes au backend."""

    return get_settings().mqtt_telemetry_topic


def dashboard_events_topic() -> str:
    """Topic générique consommé par les dashboards qui n'ont besoin que d'un signal de refresh."""

    return f"{get_settings().mqtt_events_topic_prefix}/dashboard"


def measurements_events_topic() -> str:
    """Topic utilisé quand une nouvelle mesure a été persistée."""

    return f"{get_settings().mqtt_events_topic_prefix}/measurement"


def alerts_events_topic() -> str:
    """Topic utilisé quand l'état des alertes a potentiellement changé."""

    return f"{get_settings().mqtt_events_topic_prefix}/alert"
