import type { MachineStatus } from "@/lib/types";

const statusLabels: Record<MachineStatus, string> = {
  idle: "Idle",
  running: "Running",
  alert: "Alert",
  maintenance: "Maintenance",
};

export function StatusBadge({ status }: { status: MachineStatus }) {
  return <span className={`status-badge ${status}`}>{statusLabels[status]}</span>;
}
