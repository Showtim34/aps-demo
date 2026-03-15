import type { DashboardSummary } from "@/lib/types";

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  const cards = [
    { label: "Sites", value: summary.sites_count },
    { label: "Machines", value: summary.machines_count },
    { label: "Alertes actives", value: summary.active_alerts_count },
    {
      label: "Machines en alerte",
      value:
        summary.machines_by_status.find((item) => item.status === "alert")
          ?.count ?? 0,
    },
  ];

  return (
    <section className="summary-grid">
      {cards.map((card) => (
        <article className="summary-card" key={card.label}>
          <p>{card.label}</p>
          <strong>{card.value}</strong>
        </article>
      ))}
    </section>
  );
}
