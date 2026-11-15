# API reference

Base URL: `http://localhost:8000`

Auth for **writes**: header `X-API-Key` or `Authorization: Bearer <key>`. Default key: `audit_demo_key`.

Reads (search, metrics, reports) are open in this MVP so the demo dashboard works without a login. Do not expose a real deployment this way.

## Event shape

```json
{
  "model": "gpt-4o",
  "provider": "openai",
  "prompt": "...",
  "completion": "...",
  "system_prompt": "...",
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "cost_usd": null,
  "latency_ms": 0,
  "prompt_version": "v1",
  "user_id": "agent-1",
  "session_id": "sess-1",
  "tags": ["customer-support"],
  "metadata": { "channel": "ops" },
  "sources": ["retrieved doc snippet used for grounding"]
}
```

`cost_usd` is estimated from public list prices when omitted. On ingest, the versioned rubric + groundedness judge attach `failure_flags`, `quality_score`, `judge_scores`, `groundedness_score`, and seal `event_hash` into the append-only chain.

## Endpoints

- `POST /v1/events` — one event
- `POST /v1/events/batch` — `{ "events": [ ... ] }`
- `GET /v1/events?q=&model=&flag=&tag=&prompt_version=&limit=&offset=`
- `GET /v1/events/{id}`
- `GET /v1/metrics?days=30`
- `GET /v1/drift`
- `GET /v1/failures?limit=40`
- `GET /v1/compare?days=30`
- `GET /v1/integrity/verify` — hash-chain status
- `POST /v1/admin/retention/run?retention_days=30` — soft-purge
- `GET /v1/rubrics`
- `GET/POST /v1/registry/models`
- `GET/POST /v1/registry/prompts`
- `GET/POST /v1/incidents`
- `PATCH /v1/incidents/{id}`
- `GET /v1/reports/eu-ai-act?format=json|html`
- `GET /v1/reports/sec?format=json|html`
- `POST /v1/trial` — `{ "email", "company", "use_case" }`
- `GET /health`

Interactive docs: `/docs` (Swagger UI).
