# Getting started (5 minutes)

1. Start the stack with `docker compose up --build` from the repo root.
2. Open http://localhost:5173 — marketing site.
3. Click **Open live demo** (or `/app`) — seeded ledger, drift incident, model compare.
4. Optional: **Get started free** posts to `POST /v1/trial` and stores `audit_demo_key` in the browser.
5. Ingest your own call:

```bash
curl -s http://localhost:8000/v1/events \
  -H "X-API-Key: audit_demo_key" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"gpt-4o\",\"prompt\":\"Summarize ticket 1\",\"completion\":\"Customer wants a card replacement.\",\"prompt_tokens\":120,\"completion_tokens\":40,\"latency_ms\":800,\"prompt_version\":\"v1\",\"tags\":[\"customer-support\"]}"
```

6. Python path: `cd sdk/python && pip install -e . && python examples/log_openai.py`

If the dashboard is empty, the API has not finished seeding. Wait a few seconds and refresh.
