import type {
  AuditEvent,
  DriftResponse,
  FailuresResponse,
  Incident,
  IntegrityResponse,
  MetricsResponse,
  ModelRow,
  OversightResponse,
  OversightReview,
  RegistryModel,
  RegistryPrompt,
  ReportResponse,
  ReviewDecision,
  Rubric,
} from "./types";

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
  oversight: (params: { status?: string; limit?: number } = {}) =>
    request<OversightResponse>(`/v1/oversight${query(params)}`),
  eventReviews: (eventId: string) => request<OversightReview[]>(`/v1/oversight/events/${eventId}`),
  review: (body: { event_id: string; reviewer: string; decision: ReviewDecision; note?: string }) =>
    request<OversightReview>("/v1/oversight", { method: "POST", body: JSON.stringify(body) }),
  report: (kind: "eu-ai-act" | "sec") => request<ReportResponse>(`/v1/reports/${kind}?format=json`),
  trial: (body: { email: string; company?: string; use_case?: string }) =>
    request<{ api_key: string; message: string }>("/v1/trial", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  integrity: () => request<IntegrityResponse>("/v1/integrity/verify"),
  retention: (retention_days?: number) =>
    request<{ purged: number; retention_days: number; note: string; cutoff: string }>(
      `/v1/admin/retention/run${retention_days != null ? `?retention_days=${retention_days}` : ""}`,
      { method: "POST" },
    ),
  rubrics: () => request<{ rubrics: Rubric[] }>("/v1/rubrics"),
  models: () => request<{ models: RegistryModel[] }>("/v1/registry/models"),
  prompts: () => request<{ prompts: RegistryPrompt[] }>("/v1/registry/prompts"),
  saveModel: (body: Partial<RegistryModel> & { name: string }) =>
    request<RegistryModel>("/v1/registry/models", { method: "POST", body: JSON.stringify(body) }),
  savePrompt: (body: Partial<RegistryPrompt> & { version: string }) =>
    request<RegistryPrompt>("/v1/registry/prompts", { method: "POST", body: JSON.stringify(body) }),
  incidents: (status?: string) =>
    request<{ incidents: Incident[] }>(`/v1/incidents${status ? `?status=${status}` : ""}`),
  createIncident: (body: Partial<Incident> & { title: string }) =>
    request<Incident>("/v1/incidents", { method: "POST", body: JSON.stringify(body) }),
  patchIncident: (id: string, body: Partial<Incident>) =>
    request<Incident>(`/v1/incidents/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
};
