import type { AuditEvent, DriftResponse, FailuresResponse, MetricsResponse, ModelRow, ReportResponse } from "./types";

export const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function getApiKey() {
  return localStorage.getItem("audit_api_key") || "audit_demo_key";
}

export function setApiKey(key: string) {
  localStorage.setItem("audit_api_key", key);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("X-API-Key", getApiKey());
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiBase + path, { ...init, headers });
  if (!res.ok) {
    throw new Error((await res.text()) || res.statusText);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("text/html")) return (await res.text()) as T;
  return res.json() as Promise<T>;
}

function query(params: Record<string, string | number | undefined>) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") q.set(key, String(value));
  });
  const s = q.toString();
  return s ? `?${s}` : "";
}

export const api = {
  metrics: (days = 30) => request<MetricsResponse>(`/v1/metrics?days=${days}`),
  events: (params: Record<string, string | number | undefined> = {}) =>
    request<{ total: number; events: AuditEvent[] }>(`/v1/events${query(params)}`),
  event: (id: string) => request<AuditEvent>(`/v1/events/${id}`),
  drift: () => request<DriftResponse>("/v1/drift"),
  failures: () => request<FailuresResponse>("/v1/failures"),
  compare: (days = 30) => request<{ days: number; models: ModelRow[] }>(`/v1/compare?days=${days}`),
  report: (kind: "eu-ai-act" | "sec") => request<ReportResponse>(`/v1/reports/${kind}?format=json`),
  trial: (body: { email: string; company?: string; use_case?: string }) =>
    request<{ api_key: string; message: string }>("/v1/trial", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
