export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type LoginPayload = {
  email: string;
  password: string;
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
  status: "idle" | "running" | "alert" | "maintenance";
  created_at: string;
};

export type SitePayload = {
  name: string;
  city: string;
  country: string;
};

export type MachinePayload = {
  site_id: number;
  code: string;
  name: string;
  machine_type: string;
  status: "idle" | "running" | "alert" | "maintenance";
};

export type MeasurementPayload = {
  machine_id: number;
  temperature: number;
  vibration: number;
  power: number;
};

export type SeedResponse = {
  message: string;
  admin_email: string;
  admin_password: string;
};
