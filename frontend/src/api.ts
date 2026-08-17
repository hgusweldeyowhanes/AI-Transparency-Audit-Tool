export type AuditEvent = {
  id: string;
  timestamp: string;
  trace_id: string;
  model: string;
  provider: string;
  prompt: string;
  completion: string;
  system_prompt?: string | null;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number;
  latency_ms: number;
  prompt_version?: string | null;
  user_id?: string | null;
  session_id?: string | null;
  tags: string[];
  metadata: Record<string, unknown>;
  failure_flags: string[];
  quality_score: number;
};

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function getApiKey() {
  return localStorage.getItem("audit_api_key") || "audit_demo_key";
}

export function setApiKey(key: string) {
  localStorage.setItem("audit_api_key", key);
}

async function request(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("X-API-Key", getApiKey());
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(API + path, { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("text/html")) return res.text();
  return res.json();
}

export const api = {
  health: () => request("/health"),
  metrics: (days = 30) => request(`/v1/metrics?days=${days}`),
  events: (params: Record<string, string | number | undefined> = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") q.set(k, String(v));
    });
    return request(`/v1/events?${q.toString()}`) as Promise<{ total: number; events: AuditEvent[] }>;
  },
  event: (id: string) => request(`/v1/events/${id}`) as Promise<AuditEvent>,
  drift: () => request("/v1/drift"),
  failures: () => request("/v1/failures"),
  compare: (days = 30) => request(`/v1/compare?days=${days}`),
  report: (kind: "eu-ai-act" | "sec", format: "json" | "html" = "json") =>
    request(`/v1/reports/${kind}?format=${format}`),
  trial: (body: { email: string; company?: string; use_case?: string }) =>
    request("/v1/trial", { method: "POST", body: JSON.stringify(body) }),
};

export const apiBase = API;
