import mqtt, { MqttClient } from "mqtt";

type MeasurementScenario = {
  machine_id: number;
  temperature: number;
  vibration: number;
  power: number;
};

const MQTT_WS_URL = process.env.NEXT_PUBLIC_MQTT_WS_URL ?? "ws://localhost:9001";
const TELEMETRY_TOPIC = "monitor/telemetry/measurements";

export function connectOpsPublisher(onStatus: (status: string) => void): MqttClient {
  const client = mqtt.connect(MQTT_WS_URL, {
    clientId: `factory-monitor-ops-${Math.random().toString(16).slice(2, 10)}`,
    reconnectPeriod: 2000,
  });

  client.on("connect", () => onStatus("Connecte au broker MQTT"));
  client.on("reconnect", () => onStatus("Reconnexion MQTT..."));
  client.on("error", (error) => onStatus(`Erreur MQTT: ${error.message}`));

  return client;
}

export function publishScenario(client: MqttClient, payload: MeasurementScenario) {
  client.publish(TELEMETRY_TOPIC, JSON.stringify(payload), { qos: 0 });
}
