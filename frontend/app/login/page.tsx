"use client";

import { LoginForm } from "@/components/dashboard/LoginForm";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div>
          <p className="eyebrow">APS Lab Monitor</p>
          <h1>Console d&apos;administration</h1>
          <p className="muted">
            Connectez-vous avec le compte de démonstration pour superviser les
            sites, machines, mesures et alertes.
          </p>
        </div>
        <LoginForm />
      </section>
    </main>
  );
}
