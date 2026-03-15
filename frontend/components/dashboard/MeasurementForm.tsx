"use client";

import { FormEvent, useState } from "react";

import { getStoredToken } from "@/lib/auth";
import { apiClient } from "@/lib/api";

type MeasurementFormProps = {
  machineId: number;
  onMeasurementCreated: () => Promise<void>;
};

export function MeasurementForm({
  machineId,
  onMeasurementCreated,
}: MeasurementFormProps) {
  const [temperature, setTemperature] = useState("72");
  const [vibration, setVibration] = useState("4.2");
  const [power, setPower] = useState("68");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getStoredToken();
    if (!token) {
      setError("Session expirée.");
      return;
    }

    try {
      setLoading(true);
      await apiClient.createMeasurement(token, {
        machine_id: machineId,
        temperature: Number(temperature),
        vibration: Number(vibration),
        power: Number(power),
      });
      setError(null);
      await onMeasurementCreated();
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Mesure impossible à enregistrer",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <article className="panel">
      <h2>Ajouter une mesure</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Température
          <input
            onChange={(event) => setTemperature(event.target.value)}
            type="number"
            value={temperature}
          />
        </label>
        <label>
          Vibration
          <input
            onChange={(event) => setVibration(event.target.value)}
            step="0.1"
            type="number"
            value={vibration}
          />
        </label>
        <label>
          Puissance
          <input
            onChange={(event) => setPower(event.target.value)}
            type="number"
            value={power}
          />
        </label>
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-button" disabled={loading} type="submit">
          {loading ? "Enregistrement..." : "Enregistrer la mesure"}
        </button>
      </form>
    </article>
  );
}
