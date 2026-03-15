"use client";

import { LoginPanel } from "@/components/LoginPanel";

export default function LoginPage() {
  return (
    <main className="login-page">
      <section className="login-card">
        <div>
          <p className="eyebrow">Factory Ops</p>
          <h1>Console d&apos;actions</h1>
          <p className="muted">
            Interface dédiée à l&apos;injection de données de démonstration, à la
            création de machines et au déclenchement d&apos;alertes via l&apos;API.
          </p>
        </div>
        <LoginPanel />
      </section>
    </main>
  );
}
