export type MachineStatus = "idle" | "running" | "alert" | "maintenance";
export type AlertLevel = "warning" | "critical";

export type LoginPayload = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type Site = {
  id: number;
  name: string;
  city: string;
  country: string;
  created_at: string;
};

export type Machine = {
  id: number;
  site_id: number;
  code: string;
  name: string;
  machine_type: string;
  status: MachineStatus;
  created_at: string;
};

export type MachineDetail = Machine & {
  site: Site;
};

export type Measurement = {
  id: number;
  machine_id: number;
  temperature: number;
  vibration: number;
  power: number;
  recorded_at: string;
};

export type Alert = {
  id: number;
  machine_id: number;
  level: AlertLevel;
  message: string;
  is_active: boolean;
  created_at: string;
};

export type StatusCount = {
  status: MachineStatus;
  count: number;
};

export type DashboardSummary = {
  sites_count: number;
  machines_count: number;
  active_alerts_count: number;
  machines_by_status: StatusCount[];
  recent_measurements: Measurement[];
  sites: Site[];
  machines: Machine[];
  active_alerts: Alert[];
};

export type MqttDashboardEvent = {
  kind: string;
  machine_id: number | null;
  reason: string;
  summary?: DashboardSummary;
};

export type MachineFilters = {
  siteId?: number;
  status?: MachineStatus;
};

export type MeasurementPayload = {
  machine_id: number;
  temperature: number;
  vibration: number;
  power: number;
};
