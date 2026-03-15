import type {
  LoginPayload,
  Machine,
  MachinePayload,
  MeasurementPayload,
  SeedResponse,
  Site,
  SitePayload,
  TokenResponse,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail =
      body && typeof body.detail === "string"
        ? body.detail
        : `HTTP ${response.status}`;
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  login(payload: LoginPayload) {
    return request<TokenResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  listSites(token: string) {
    return request<Site[]>("/api/v1/sites", {}, token);
  },
  createSite(token: string, payload: SitePayload) {
    return request<Site>("/api/v1/sites", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token);
  },
  listMachines(token: string) {
    return request<Machine[]>("/api/v1/machines", {}, token);
  },
  createMachine(token: string, payload: MachinePayload) {
    return request<Machine>("/api/v1/machines", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token);
  },
  createMeasurement(token: string, payload: MeasurementPayload) {
    return request("/api/v1/measurements", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token);
  },
  seedDemo(token: string) {
    return request<SeedResponse>("/api/v1/demo/seed", { method: "POST" }, token);
  },
};
