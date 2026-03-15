import type { Alert } from "@/lib/types";

export function AlertsList({ alerts }: { alerts: Alert[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Alertes actives</h2>
          <p className="muted">
            Les alertes sont générées automatiquement à partir des mesures.
          </p>
        </div>
      </div>
      <div className="alerts-list">
        {alerts.length === 0 ? (
          <p className="muted">Aucune alerte active.</p>
        ) : (
          alerts.map((alert) => (
            <article className={`alert-card ${alert.level}`} key={alert.id}>
              <div>
                <p className="alert-title">
                  Machine #{alert.machine_id} · {alert.level}
                </p>
                <p>{alert.message}</p>
              </div>
              <span>{new Date(alert.created_at).toLocaleString("fr-FR")}</span>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
