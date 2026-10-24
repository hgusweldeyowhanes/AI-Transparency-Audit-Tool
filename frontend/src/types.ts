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

export type SeriesPoint = {
  date: string;
  events: number;
  failure_rate: number;
  cost_usd: number;
  factual_error_rate?: number;
  avg_latency_ms?: number;
};

export type WindowStats = {
  events: number;
  failed: number;
  failure_rate: number;
  avg_latency_ms: number;
  avg_cost_usd: number;
  avg_quality: number;
  total_cost_usd?: number;
};

export type MetricsResponse = {
  days: number;
  events: number;
  failed_events: number;
  failure_rate: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  avg_quality: number;
  series: SeriesPoint[];
};

export type DriftResponse = {
  current_window: { start: string; end: string; stats: WindowStats };
  previous_window: { start: string; end: string; stats: WindowStats };
  deltas: Record<string, number | null>;
  series: SeriesPoint[];
  incidents: { date: string; title: string; detail: string }[];
};

export type ModelRow = {
  model: string;
  provider: string;
  events: number;
  failure_rate: number;
  total_cost_usd: number;
  avg_cost_usd: number;
  avg_latency_ms: number;
  avg_quality: number;
  cost_per_quality: number;
};

export type FailuresResponse = {
  scanned: number;
  failed_events: number;
  taxonomy: { flag: string; label: string; count: number }[];
  clusters: { flag: string; count: number; sample: string; event_ids: string[] }[];
};

export type ReviewDecision = "confirmed" | "false_positive" | "escalated" | "cleared";

export type OversightReview = {
  id: string;
  event_id: string;
  created_at: string;
  reviewer: string;
  decision: ReviewDecision;
  note: string;
};

export type OversightStats = {
  flagged_events: number;
  reviewed: number;
  pending: number;
  coverage: number;
  confirmed: number;
  false_positive: number;
  escalated: number;
  cleared: number;
};

export type OversightQueueItem = {
  id: string;
  timestamp: string;
  model: string;
  prompt_version?: string | null;
  failure_flags: string[];
  quality_score: number;
  prompt: string;
  completion: string;
  review: OversightReview | null;
};

export type OversightResponse = {
  stats: OversightStats;
  queue: OversightQueueItem[];
  recent: OversightReview[];
};

export const DECISION_LABEL: Record<ReviewDecision, string> = {
  confirmed: "Confirmed failure",
  false_positive: "False positive",
  escalated: "Escalated",
  cleared: "Cleared",
};

export type ReportResponse = {
  title: string;
  disclaimer: string;
  generated_at: string;
  human_oversight?: OversightStats;
  inventory: {
    event_count: number;
    retention_days: number;
    models: ModelRow[];
  };
};

export const MODELS = ["gpt-4o", "claude-3-5-sonnet", "llama-3.1-70b"] as const;

export const FLAGS = [
  "factual_error",
  "empty",
  "refusal",
  "knowledge_gap",
  "hedging",
  "pii_leak",
  "latency_anomaly",
  "truncated",
] as const;
