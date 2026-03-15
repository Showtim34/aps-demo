"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export function LoginPanel() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      setLoading(true);
      const response = await api.login({ email, password });
      saveToken(response.access_token);
      router.replace("/operations");
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Connexion impossible",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <label>
        Email
        <input
          onChange={(event) => setEmail(event.target.value)}
          type="email"
          value={email}
        />
      </label>
      <label>
        Mot de passe
        <input
          onChange={(event) => setPassword(event.target.value)}
          type="password"
          value={password}
        />
      </label>
      {error ? <p className="error-text">{error}</p> : null}
      <button className="primary-button" disabled={loading} type="submit">
        {loading ? "Connexion..." : "Entrer dans la console"}
      </button>
    </form>
  );
}
