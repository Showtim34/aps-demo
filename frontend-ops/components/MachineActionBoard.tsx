"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { connectOpsPublisher, publishScenario } from "@/lib/mqtt";
import type { Machine, Site } from "@/lib/types";

type Props = {
  machines: Machine[];
  sites: Site[];
  onDone: () => Promise<void>;
};

export function MachineActionBoard({ machines, sites, onDone }: Props) {
  const [selectedMachineId, setSelectedMachineId] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mqttStatus, setMqttStatus] = useState("Connexion MQTT en attente...");
  const mqttClientRef = useRef<ReturnType<typeof connectOpsPublisher> | null>(null);
  const siteMap = useMemo(
    () => new Map(sites.map((site) => [site.id, site.name])),
    [sites],
  );

  useEffect(() => {
    const client = connectOpsPublisher(setMqttStatus);
    mqttClientRef.current = client;
    return () => {
      client.end(true);
      mqttClientRef.current = null;
    };
  }, []);

  async function submitScenario(kind: "warning" | "critical" | "normal") {
    if (!selectedMachineId) {
      setError("Choisis une machine avant d'envoyer une mesure.");
      return;
    }
    if (!mqttClientRef.current) {
      setError("Client MQTT non disponible.");
      return;
    }

    const payloadByKind = {
      warning: { temperature: 84, vibration: 6.5, power: 91 },
      critical: { temperature: 99, vibration: 8.9, power: 100 },
      normal: { temperature: 71, vibration: 3.2, power: 64 },
    };

    try {
      publishScenario(mqttClientRef.current, {
        machine_id: Number(selectedMachineId),
        ...payloadByKind[kind],
      });
      setMessage(
        kind === "normal"
          ? "Mesure MQTT normale envoyée. Les alertes actives de la machine doivent être fermees."
          : `Mesure MQTT ${kind} envoyee. Une alerte doit apparaitre sur le dashboard.`,
      );
      setError(null);
      window.setTimeout(() => {
        void onDone();
      }, 600);
    } catch (submitError) {
      setMessage(null);
      setError(
        submitError instanceof Error ? submitError.message : "Envoi impossible",
      );
    }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>Déclencher un scénario machine</h2>
          <p className="muted">
            L&apos;API ne crée pas d&apos;alerte directement. Elle la déduit d&apos;une
            mesure. Cette console publie donc des mesures sur MQTT, puis le
            backend Python les consomme et applique les regles metier.
          </p>
        </div>
      </div>
      <p className="muted">Etat MQTT : {mqttStatus}</p>

      <div className="scenario-grid">
        <label>
          Machine ciblée
          <select
            onChange={(event) => setSelectedMachineId(event.target.value)}
            value={selectedMachineId}
          >
            <option value="">Choisir une machine</option>
            {machines.map((machine) => (
              <option key={machine.id} value={machine.id}>
                {machine.code} · {machine.name} · {siteMap.get(machine.site_id)}
              </option>
            ))}
          </select>
        </label>

        <div className="button-row">
          <button
            className="warning-button"
            onClick={() => void submitScenario("warning")}
            type="button"
          >
            Publier warning MQTT
          </button>
          <button
            className="danger-button"
            onClick={() => void submitScenario("critical")}
            type="button"
          >
            Publier critical MQTT
          </button>
          <button
            className="success-button"
            onClick={() => void submitScenario("normal")}
            type="button"
          >
            Publier normal MQTT
          </button>
        </div>
      </div>

      {message ? <p className="success-text">{message}</p> : null}
      {error ? <p className="error-text">{error}</p> : null}

      <div className="machine-table">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Nom</th>
              <th>Site</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {machines.map((machine) => (
              <tr key={machine.id}>
                <td>{machine.code}</td>
                <td>{machine.name}</td>
                <td>{siteMap.get(machine.site_id) ?? `Site #${machine.site_id}`}</td>
                <td>
                  <span className={`status-pill ${machine.status}`}>
                    {machine.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
