"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { persistToken } from "@/lib/auth";
import { apiClient } from "@/lib/api";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      setLoading(true);
      const response = await apiClient.login({ email, password });
      persistToken(response.access_token);
      router.replace("/dashboard");
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Connexion impossible",
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
          autoComplete="email"
          onChange={(event) => setEmail(event.target.value)}
          type="email"
          value={email}
        />
      </label>
      <label>
        Mot de passe
        <input
          autoComplete="current-password"
          onChange={(event) => setPassword(event.target.value)}
          type="password"
          value={password}
        />
      </label>
      {error ? <p className="error-text">{error}</p> : null}
      <button className="primary-button" disabled={loading} type="submit">
        {loading ? "Connexion..." : "Se connecter"}
      </button>
      <p className="helper-text">
        Compte de démo : <strong>admin@example.com</strong> /{" "}
        <strong>admin123</strong>
      </p>
    </form>
  );
}
