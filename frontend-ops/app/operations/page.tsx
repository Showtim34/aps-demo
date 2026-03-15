"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CreateMachineForm } from "@/components/CreateMachineForm";
import { CreateSiteForm } from "@/components/CreateSiteForm";
import { MachineActionBoard } from "@/components/MachineActionBoard";
import { clearToken, getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import type { Machine, Site } from "@/lib/types";

export default function OperationsPage() {
  const router = useRouter();
  const [sites, setSites] = useState<Site[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [seedMessage, setSeedMessage] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }
    void loadData(token);
  }, [router]);

  async function loadData(token: string) {
    try {
      setLoading(true);
      const [nextSites, nextMachines] = await Promise.all([
        api.listSites(token),
        api.listMachines(token),
      ]);
      setSites(nextSites);
      setMachines(nextMachines);
      setError(null);
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setLoading(false);
    }
  }

  function handleError(loadError: unknown) {
    const message =
      loadError instanceof Error ? loadError.message : "Erreur inattendue";
    if (message.toLowerCase().includes("401")) {
      clearToken();
      router.replace("/login");
      return;
    }
    setError(message);
  }

  async function refresh() {
    const token = getToken();
    if (!token) {
      return;
    }
    await loadData(token);
  }

  async function triggerSeed() {
    const token = getToken();
    if (!token) {
      return;
    }
    try {
      const result = await api.seedDemo(token);
      setSeedMessage(
        `${result.message} - admin ${result.admin_email} / ${result.admin_password}`,
      );
      await refresh();
    } catch (seedError) {
      handleError(seedError);
    }
  }

  if (loading) {
    return <main className="center-shell">Chargement des opérations...</main>;
  }

  return (
    <main className="ops-shell">
      <header className="ops-header">
        <div>
          <p className="eyebrow">APS Lab Ops</p>
          <h1>Pilotage des injections</h1>
          <p className="muted">
            Cette interface ne remplace pas le dashboard. Elle sert à alimenter
            l&apos;API et provoquer rapidement des scénarios métier.
          </p>
        </div>
        <div className="header-actions">
          <button className="outline-button" onClick={triggerSeed} type="button">
            Lancer le seed
          </button>
          <button
            className="ghost-button"
            onClick={() => {
              clearToken();
              router.replace("/login");
            }}
            type="button"
          >
            Déconnexion
          </button>
        </div>
      </header>

      {seedMessage ? <p className="info-banner">{seedMessage}</p> : null}
      {error ? <p className="error-banner">{error}</p> : null}

      <section className="ops-grid">
        <CreateSiteForm onCreated={refresh} />
        <CreateMachineForm onCreated={refresh} sites={sites} />
      </section>

      <MachineActionBoard machines={machines} sites={sites} onDone={refresh} />
    </main>
  );
}
