"use client";

import { FormEvent, useState } from "react";

import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import type { Site } from "@/lib/types";

type Props = {
  sites: Site[];
  onCreated: () => Promise<void>;
};

export function CreateMachineForm({ sites, onCreated }: Props) {
  const [siteId, setSiteId] = useState<string>("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [machineType, setMachineType] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getToken();
    if (!token) {
      setError("Session expirée.");
      return;
    }
    try {
      await api.createMachine(token, {
        site_id: Number(siteId),
        code,
        name,
        machine_type: machineType,
        status: "idle",
      });
      setCode("");
      setName("");
      setMachineType("");
      setMessage("Machine créée.");
      setError(null);
      await onCreated();
    } catch (submitError) {
      setMessage(null);
      setError(
        submitError instanceof Error ? submitError.message : "Création impossible",
      );
    }
  }

  return (
    <section className="panel">
      <h2>Créer une machine</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Site
          <select onChange={(event) => setSiteId(event.target.value)} value={siteId}>
            <option value="">Choisir un site</option>
            {sites.map((site) => (
              <option key={site.id} value={site.id}>
                {site.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Code unique
          <input onChange={(event) => setCode(event.target.value)} value={code} />
        </label>
        <label>
          Nom
          <input onChange={(event) => setName(event.target.value)} value={name} />
        </label>
        <label>
          Type
          <input
            onChange={(event) => setMachineType(event.target.value)}
            value={machineType}
          />
        </label>
        {message ? <p className="success-text">{message}</p> : null}
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-button" disabled={!siteId} type="submit">
          Ajouter la machine
        </button>
      </form>
    </section>
  );
}
