"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { MachineChart } from "@/components/dashboard/MachineChart";
import { MeasurementForm } from "@/components/dashboard/MeasurementForm";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { clearStoredToken, getStoredToken } from "@/lib/auth";
import { apiClient } from "@/lib/api";
import type { MachineDetail, Measurement } from "@/lib/types";

export default function MachineDetailPage() {
  const params = useParams<{ machineId: string }>();
  const router = useRouter();
  const [machine, setMachine] = useState<MachineDetail | null>(null);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }
    void loadMachineData(token);
  }, [params.machineId, router]);

  async function loadMachineData(token: string) {
    try {
      setLoading(true);
      const [machineDetail, machineMeasurements] = await Promise.all([
        apiClient.getMachine(token, Number(params.machineId)),
        apiClient.listMachineMeasurements(token, Number(params.machineId)),
      ]);
      setMachine(machineDetail);
      setMeasurements(machineMeasurements);
      setError(null);
    } catch (loadError) {
      const message =
        loadError instanceof Error ? loadError.message : "Erreur inattendue";
      if (message.toLowerCase().includes("401")) {
        clearStoredToken();
        router.replace("/login");
        return;
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  const latestMeasurement = useMemo(() => measurements[0], [measurements]);

  if (loading) {
    return <main className="centered-shell">Chargement de la machine...</main>;
  }

  if (!machine) {
    return <main className="centered-shell">Machine introuvable.</main>;
  }

  return (
    <main className="page-shell">
      <header className="page-header">
        <div>
          <Link className="back-link" href="/dashboard">
            Retour au dashboard
          </Link>
          <h1>{machine.name}</h1>
          <p className="muted">
            {machine.code} · {machine.machine_type} · {machine.site.name}
          </p>
        </div>
        <StatusBadge status={machine.status} />
      </header>

      {error ? <p className="error-banner">{error}</p> : null}

      <section className="detail-grid">
        <article className="panel">
          <h2>Dernière mesure</h2>
          {latestMeasurement ? (
            <dl className="metric-grid">
              <div>
                <dt>Température</dt>
                <dd>{latestMeasurement.temperature.toFixed(1)}°C</dd>
              </div>
              <div>
                <dt>Vibration</dt>
                <dd>{latestMeasurement.vibration.toFixed(1)} mm/s</dd>
              </div>
              <div>
                <dt>Puissance</dt>
                <dd>{latestMeasurement.power.toFixed(1)}%</dd>
              </div>
            </dl>
          ) : (
            <p className="muted">Aucune mesure disponible pour cette machine.</p>
          )}
        </article>

        <MeasurementForm
          machineId={machine.id}
          onMeasurementCreated={async () => {
            const token = getStoredToken();
            if (!token) {
              return;
            }
            await loadMachineData(token);
          }}
        />
      </section>

      <MachineChart measurements={measurements} />
    </main>
  );
}
