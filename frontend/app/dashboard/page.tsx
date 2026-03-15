"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { AlertsList } from "@/components/dashboard/AlertsList";
import { MachinesTable } from "@/components/dashboard/MachinesTable";
import { SummaryCards } from "@/components/dashboard/SummaryCards";
import { clearStoredToken, getStoredToken } from "@/lib/auth";
import { apiClient } from "@/lib/api";
import { connectDashboardEvents } from "@/lib/mqtt";
import type { DashboardSummary, Machine, MachineStatus, MqttDashboardEvent } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<MachineStatus | "all">(
    "all",
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [mqttStatus, setMqttStatus] = useState("Connexion MQTT en attente...");
  const mqttClientRef = useRef<ReturnType<typeof connectDashboardEvents> | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    void loadDashboard(token);
  }, [router]);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      return;
    }

    const client = connectDashboardEvents(
      (event: MqttDashboardEvent) => {
        if (event.summary) {
          setSummary(event.summary);
          setMachines(event.summary.machines);
        } else {
          void loadDashboard(token);
        }
      },
      setMqttStatus,
    );
    mqttClientRef.current = client;

    return () => {
      client.end(true);
      mqttClientRef.current = null;
    };
  }, []);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      return;
    }

    void loadMachines(token, selectedSiteId, selectedStatus);
  }, [selectedSiteId, selectedStatus]);

  async function loadDashboard(token: string) {
    try {
      setLoading(true);
      const dashboardSummary = await apiClient.getDashboardSummary(token);
      setSummary(dashboardSummary);
      setMachines(dashboardSummary.machines);
      setError(null);
    } catch (loadError) {
      handleUnauthorized(loadError);
    } finally {
      setLoading(false);
    }
  }

  async function loadMachines(
    token: string,
    siteId: string,
    status: MachineStatus | "all",
  ) {
    try {
      const filteredMachines = await apiClient.listMachines(token, {
        siteId: siteId === "all" ? undefined : Number(siteId),
        status: status === "all" ? undefined : status,
      });
      setMachines(filteredMachines);
    } catch (loadError) {
      handleUnauthorized(loadError);
    }
  }

  function handleUnauthorized(loadError: unknown) {
    const message =
      loadError instanceof Error ? loadError.message : "Une erreur est survenue.";
    if (message.toLowerCase().includes("401")) {
      clearStoredToken();
      router.replace("/login");
      return;
    }
    setError(message);
  }

  const siteOptions = useMemo(() => summary?.sites ?? [], [summary]);

  if (loading) {
    return <main className="centered-shell">Chargement du dashboard...</main>;
  }

  if (!summary) {
    return <main className="centered-shell">Aucune donnée disponible.</main>;
  }

  return (
    <main className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">APS Lab Monitor</p>
          <h1>Dashboard de supervision</h1>
          <p className="muted">
            Vue synthétique des sites, machines, alertes actives et dernières
            mesures.
          </p>
        </div>
        <button
          className="secondary-button"
          onClick={() => {
            clearStoredToken();
            router.replace("/login");
          }}
          type="button"
        >
          Se déconnecter
        </button>
      </header>

      {error ? <p className="error-banner">{error}</p> : null}
      <p className="helper-text">Temps reel MQTT : {mqttStatus}</p>

      <SummaryCards summary={summary} />

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Machines</h2>
            <p className="muted">
              Filtrage rapide par site et par statut avant accès au détail.
            </p>
          </div>
          <div className="filters">
            <label>
              Site
              <select
                value={selectedSiteId}
                onChange={(event) => setSelectedSiteId(event.target.value)}
              >
                <option value="all">Tous</option>
                {siteOptions.map((site) => (
                  <option key={site.id} value={site.id}>
                    {site.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Statut
              <select
                value={selectedStatus}
                onChange={(event) =>
                  setSelectedStatus(event.target.value as MachineStatus | "all")
                }
              >
                <option value="all">Tous</option>
                <option value="idle">Idle</option>
                <option value="running">Running</option>
                <option value="alert">Alert</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </label>
          </div>
        </div>
        <MachinesTable machines={machines} sites={summary.sites} />
      </section>

      <AlertsList alerts={summary.active_alerts} />
    </main>
  );
}
