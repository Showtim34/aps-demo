"""Intégration MQTT pour ingérer la télémétrie et publier des événements.

Ce module utilise `paho-mqtt`, un client Python classique pour les brokers
MQTT.

Responsabilités :

- s'abonner aux messages de télémétrie entrants
- les convertir en mesures applicatives normales
- publier des événements légers pour que l'interface réagisse en temps réel
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.realtime import topics

logger = get_logger(__name__)
settings = get_settings()


@dataclass(slots=True)
class DashboardEvent:
    """Petit payload publié quand le dashboard doit se rafraîchir."""

    kind: str
    machine_id: int | None
    reason: str


class MqttRuntime:
    """Encapsule un client MQTT exécuté dans des threads d'arrière-plan.

    Paho gère les entrées/sorties réseau dans sa propre boucle. L'application
    garde ce wrapper pour éviter que le reste du code manipule directement les
    callbacks MQTT bas niveau.
    """

    def __init__(self) -> None:
        self.client: mqtt.Client | None = None
        self.started = False

    def start(self) -> None:
        """Se connecte au broker et s'abonne aux topics de télémétrie."""

        if self.started or not settings.mqtt_enabled:
            return

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="aps-lab-api")
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect
        client.connect_async(settings.mqtt_host, settings.mqtt_port, keepalive=30)
        client.loop_start()
        self.client = client
        self.started = True
        logger.info(
            "MQTT runtime started on %s:%s and waiting for telemetry",
            settings.mqtt_host,
            settings.mqtt_port,
        )

    def stop(self) -> None:
        """Arrête proprement la boucle MQTT en arrière-plan."""

        if self.client is None:
            return
        self.client.loop_stop()
        self.client.disconnect()
        self.client = None
        self.started = False

    def publish_dashboard_event(
        self, *, kind: str, machine_id: int | None, reason: str, summary: dict[str, Any] | None = None
    ) -> None:
        """Publie les événements MQTT génériques et spécifiques après un changement métier."""

        if self.client is None:
            return

        payload = {"kind": kind, "machine_id": machine_id, "reason": reason}
        if summary is not None:
            payload["summary"] = summary

        self.client.publish(topics.dashboard_events_topic(), json.dumps(payload), qos=0)
        if kind == "measurement":
            self.client.publish(topics.measurements_events_topic(), json.dumps(payload), qos=0)
        if kind == "alert":
            self.client.publish(topics.alerts_events_topic(), json.dumps(payload), qos=0)

    def _on_connect(
        self,
        client: mqtt.Client,
        _: Any,
        __: Any,
        reason_code: mqtt.ReasonCode,
        ___: Any,
    ) -> None:
        if reason_code.value != 0:
            logger.warning("MQTT connection returned non-success code %s", reason_code)
            return
        client.subscribe(topics.telemetry_topic(), qos=0)
        logger.info("Subscribed to telemetry topic %s", topics.telemetry_topic())

    def _on_disconnect(
        self,
        _: mqtt.Client,
        __: Any,
        ___: Any,
        reason_code: mqtt.ReasonCode,
        ____: Any,
    ) -> None:
        logger.info("MQTT client disconnected with code %s", reason_code)

    def _on_message(
        self,
        _: mqtt.Client,
        __: Any,
        message: mqtt.MQTTMessage,
    ) -> None:
        """Reçoit la télémétrie via MQTT et réutilise la couche de service normale.

        Choix de conception important :

        On n'écrit pas directement en base ici. On reconstruit le même schéma
        `MeasurementCreate` puis on appelle `MeasurementService` afin que HTTP
        et MQTT suivent exactement les mêmes règles métier.
        """

        try:
            raw_payload = json.loads(message.payload.decode("utf-8"))
            from app.schemas.measurement import MeasurementCreate

            payload = MeasurementCreate.model_validate(raw_payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Invalid MQTT telemetry payload: %s", exc)
            return

        db = SessionLocal()
        try:
            from app.services.dashboard_service import DashboardService
            from app.services.measurement_service import MeasurementService

            measurement = MeasurementService(db).create_measurement(
                payload,
                publish_event=False,
            )
            summary = DashboardService(db).get_summary().model_dump(mode="json")
            self.publish_dashboard_event(
                kind="measurement",
                machine_id=measurement.machine_id,
                reason="mqtt_telemetry_ingested",
                summary=summary,
            )
            logger.info("MQTT telemetry ingested for machine_id=%s", measurement.machine_id)
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("Failed to process MQTT message: %s", exc)
        finally:
            db.close()


mqtt_runtime = MqttRuntime()
