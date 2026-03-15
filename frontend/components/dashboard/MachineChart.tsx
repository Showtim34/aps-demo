"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { Measurement } from "@/lib/types";

export function MachineChart({ measurements }: { measurements: Measurement[] }) {
  const chartData = [...measurements]
    .reverse()
    .map((measurement) => ({
      time: new Date(measurement.recorded_at).toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
      temperature: measurement.temperature,
      vibration: measurement.vibration,
      power: measurement.power,
    }));

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Historique des mesures</h2>
          <p className="muted">
            Courbes simples pour visualiser les dernières valeurs reçues.
          </p>
        </div>
      </div>
      <div className="chart-shell">
        <ResponsiveContainer height={320} width="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="4 4" stroke="#d8deea" />
            <XAxis dataKey="time" stroke="#526070" />
            <YAxis stroke="#526070" />
            <Tooltip />
            <Legend />
            <Line dataKey="temperature" name="Température" stroke="#d94b3d" type="monotone" />
            <Line dataKey="vibration" name="Vibration" stroke="#0d8abc" type="monotone" />
            <Line dataKey="power" name="Puissance" stroke="#17603a" type="monotone" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
