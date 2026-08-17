# audit-ai

**Prove your LLM is safe and transparent.**

Open-source, LLM-native audit trail built for regulatory compliance — not a monitoring product with a compliance sticker. Log every model decision, catch drift when a prompt version goes sideways, and export EU AI Act / SEC-style evidence packs.

> Positioning: *audit-ai is the only open-source, LLM-native audit trail platform built for regulatory compliance. We help organizations prove their AI systems are safe, fair, and transparent.*

This repository is a **self-hosted MVP**. Managed cloud, SSO, and billing are out of scope. Reports are **templates, not legal advice**.

## Why it exists

Organizations shipping LLMs cannot easily show regulators (EU AI Act, SEC-style disclosure) that systems are logged, reviewable, and stable. Secondary pain: no standard way to debug why outputs changed, 200+ hour audits, silent quality decay, and no cost-vs-quality comparison on *your* traffic.

## Features (this MVP)

- Ingest API + Python SDK (~15 minutes to wrap a call)
- Searchable event ledger (prompt, completion, model, tokens, cost, `prompt_version`)
- Heuristic failure flags: empty, refusal, knowledge gap, ungrounded citation, PII-like strings, latency/length anomalies
- Drift: last 7 days vs prior 7, plus factual-error incidents
- Failure clustering
- Model compare (cost, quality, latency)
- EU AI Act logging pack and SEC disclosure pack (HTML + JSON)
- Marketing site: landing, pricing, ROI calculator, docs, blog, resources, trial form
- Seeded demo (~520 support-summarization events, including a prompt-v2 regression)

## Quick start

```bash
docker compose up --build
```

| Surface | URL |
|---|---|
| Marketing + dashboard | http://localhost:5173 |
| API | http://localhost:8000 |
| OpenAPI | http://localhost:8000/docs |

Demo API key: `audit_demo_key` (header `X-API-Key`).

### Local (no Docker)

```bash
# API — Python 3.9+
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# UI
cd frontend
npm install
npm run dev
```

Seed data is created on first API boot if the SQLite file is empty.

## Python SDK

```bash
cd sdk/python
pip install -e .
python examples/log_openai.py
```

```python
from audit_ai import AuditClient

client = AuditClient(api_key="audit_demo_key", base_url="http://localhost:8000")

with client.trace(model="gpt-4o", prompt=user_msg, tags=["support"]) as span:
    result = llm.complete(user_msg)
    span.log(
        completion=result.text,
        prompt_tokens=result.input_tokens,
        completion_tokens=result.output_tokens,
    )
```

## API (short)

| Method | Path | Notes |
|---|---|---|
| POST | `/v1/events` | Ingest (API key) |
| POST | `/v1/events/batch` | Batch ingest |
| GET | `/v1/events` | Search |
| GET | `/v1/metrics` | Volume / cost / failure rate |
| GET | `/v1/drift` | Windows + incidents |
| GET | `/v1/failures` | Taxonomy + clusters |
| GET | `/v1/compare` | Models |
| GET | `/v1/reports/eu-ai-act?format=html` | Logging pack |
| GET | `/v1/reports/sec?format=html` | Disclosure pack |
| POST | `/v1/trial` | Capture email → demo key |

## Pricing (from the GTM)

| Plan | Price | Notes |
|---|---|---|
| Free (self-hosted) | $0 | Unlimited events, 30-day retention, community support |
| Growth | $500–$1K / mo | 10M events, 1-year retention |
| Pro | $2K–$5K / mo | Clustering, compare, 2-year retention |
| Enterprise | Custom | Residency, SSO, MSA |

This MVP implements the **free self-hosted** product. Paid tiers are described on the pricing page.

## Competitive line

- vs Arize: they monitor ML; we log LLMs for compliance
- vs Fiddler: they are enterprise-only; we are developer-first and affordable
- vs Datadog: they monitor everything; we specialize in LLM governance

## Layout

```
backend/     FastAPI + SQLite
frontend/    React (Vite) marketing site + dashboard
sdk/python/  audit_ai client
docs/        Getting started, API, compliance notes
```

## Disclaimer

Detectors are heuristics. Compliance HTML is an engineering evidence template. Nothing here is a certification, a DLP product, or counsel.

Apache-2.0 · see [LICENSE](LICENSE)
