import mqtt, { MqttClient } from "mqtt";

import type { MqttDashboardEvent } from "@/lib/types";

const MQTT_WS_URL = process.env.NEXT_PUBLIC_MQTT_WS_URL ?? "ws://localhost:9001";
const DASHBOARD_TOPIC = "aps/events/dashboard";

export function connectDashboardEvents(
  onEvent: (event: MqttDashboardEvent) => void,
  onStatus: (status: string) => void,
): MqttClient {
  const client = mqtt.connect(MQTT_WS_URL, {
    clientId: `aps-lab-front-${Math.random().toString(16).slice(2, 10)}`,
    reconnectPeriod: 2000,
  });

  client.on("connect", () => {
    onStatus("Connecte au broker MQTT");
    client.subscribe(DASHBOARD_TOPIC);
  });

  client.on("reconnect", () => {
    onStatus("Reconnexion MQTT...");
  });

  client.on("error", (error) => {
    onStatus(`Erreur MQTT: ${error.message}`);
  });

  client.on("message", (_, payload) => {
    try {
      const event = JSON.parse(payload.toString()) as MqttDashboardEvent;
      onEvent(event);
    } catch {
      onStatus("Message MQTT invalide ignore");
    }
  });

  return client;
}
