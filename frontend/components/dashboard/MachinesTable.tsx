import Link from "next/link";

import { StatusBadge } from "@/components/ui/StatusBadge";
import type { Machine, Site } from "@/lib/types";

type MachinesTableProps = {
  machines: Machine[];
  sites: Site[];
};

export function MachinesTable({ machines, sites }: MachinesTableProps) {
  const siteById = new Map(sites.map((site) => [site.id, site.name]));

  if (machines.length === 0) {
    return <p className="muted">Aucune machine ne correspond aux filtres.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Nom</th>
            <th>Type</th>
            <th>Site</th>
            <th>Statut</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {machines.map((machine) => (
            <tr key={machine.id}>
              <td>{machine.code}</td>
              <td>{machine.name}</td>
              <td>{machine.machine_type}</td>
              <td>{siteById.get(machine.site_id) ?? `Site #${machine.site_id}`}</td>
              <td>
                <StatusBadge status={machine.status} />
              </td>
              <td>
                <Link className="table-link" href={`/machines/${machine.id}`}>
                  Voir
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
