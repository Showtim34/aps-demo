import type {
  DashboardSummary,
  LoginPayload,
  Machine,
  MachineDetail,
  MachineFilters,
  Measurement,
  MeasurementPayload,
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

export const apiClient = {
  login(payload: LoginPayload) {
    return request<TokenResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getDashboardSummary(token: string) {
    return request<DashboardSummary>("/api/v1/dashboard/summary", {}, token);
  },
  listMachines(token: string, filters: MachineFilters) {
    const params = new URLSearchParams();
    if (filters.siteId) {
      params.set("site_id", String(filters.siteId));
    }
    if (filters.status) {
      params.set("status", filters.status);
    }
    const query = params.toString();
    return request<Machine[]>(
      `/api/v1/machines${query ? `?${query}` : ""}`,
      {},
      token,
    );
  },
  getMachine(token: string, machineId: number) {
    return request<MachineDetail>(`/api/v1/machines/${machineId}`, {}, token);
  },
  listMachineMeasurements(token: string, machineId: number) {
    return request<Measurement[]>(
      `/api/v1/machines/${machineId}/measurements`,
      {},
      token,
    );
  },
  createMeasurement(token: string, payload: MeasurementPayload) {
    return request<Measurement>("/api/v1/measurements", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token);
  },
};
