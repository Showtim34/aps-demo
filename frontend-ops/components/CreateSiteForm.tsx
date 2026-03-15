"use client";

import { FormEvent, useState } from "react";

import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";

export function CreateSiteForm({ onCreated }: { onCreated: () => Promise<void> }) {
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
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
      await api.createSite(token, { name, city, country });
      setName("");
      setCity("");
      setCountry("");
      setMessage("Site créé.");
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
      <h2>Créer un site</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Nom
          <input onChange={(event) => setName(event.target.value)} value={name} />
        </label>
        <label>
          Ville
          <input onChange={(event) => setCity(event.target.value)} value={city} />
        </label>
        <label>
          Pays
          <input
            onChange={(event) => setCountry(event.target.value)}
            value={country}
          />
        </label>
        {message ? <p className="success-text">{message}</p> : null}
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-button" type="submit">
          Ajouter le site
        </button>
      </form>
    </section>
  );
}
