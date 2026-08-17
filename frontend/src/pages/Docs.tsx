import { Link } from "react-router-dom";

export default function Docs() {
  return (
    <section className="section prose">
      <div className="kicker">Documentation</div>
      <h1>Five minutes to an audit trail</h1>
      <p>
        This MVP runs locally with SQLite. Demo data loads on first boot so the dashboard is never empty.
      </p>

      <h2>Quick start</h2>
      <pre className="block">{`git clone <this-repo> AI-Transparency-Audit-Tool
cd AI-Transparency-Audit-Tool
docker compose up --build
# API  http://localhost:8000
# UI   http://localhost:5173`}</pre>
      <p>Without Docker:</p>
      <pre className="block">{`# API
cd backend
python -m venv .venv
.venv\\Scripts\\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# UI
cd frontend
npm install
npm run dev`}</pre>

      <h2>Python SDK</h2>
      <pre className="block">{`from audit_ai import AuditClient

client = AuditClient(api_key="audit_demo_key", base_url="http://localhost:8000")

with client.trace(model="gpt-4o", prompt=user_msg, tags=["support"]) as span:
    result = llm.complete(user_msg)
    span.log(completion=result.text, prompt_tokens=result.input_tokens,
             completion_tokens=result.output_tokens)`}</pre>
      <p>
        Example script: <span className="mono">sdk/python/examples/log_openai.py</span> (mocks the model unless{" "}
        <span className="mono">OPENAI_API_KEY</span> is set).
      </p>

      <h2>API reference</h2>
      <ul>
        <li>
          <span className="mono">POST /v1/events</span> — ingest one event (API key required)
        </li>
        <li>
          <span className="mono">POST /v1/events/batch</span> — ingest many
        </li>
        <li>
          <span className="mono">GET /v1/events</span> — search (<span className="mono">q, model, flag, tag, prompt_version</span>)
        </li>
        <li>
          <span className="mono">GET /v1/metrics</span> — volume, cost, failure rate
        </li>
        <li>
          <span className="mono">GET /v1/drift</span> — 7-day vs prior 7-day + incidents
        </li>
        <li>
          <span className="mono">GET /v1/failures</span> — taxonomy + clusters
        </li>
        <li>
          <span className="mono">GET /v1/compare</span> — cost vs quality by model
        </li>
        <li>
          <span className="mono">GET /v1/reports/eu-ai-act?format=html</span> — logging pack template
        </li>
        <li>
          <span className="mono">GET /v1/reports/sec?format=html</span> — disclosure pack template
        </li>
      </ul>
      <p>
        Interactive OpenAPI: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a>
      </p>

      <h2>Compliance guides</h2>
      <p>
        <strong>EU AI Act.</strong> Treat the HTML pack as an Art. 12 / 13 / 14 mapping aid: what you logged, which
        models ran, failure flags, retention. It does not certify a high-risk system.
      </p>
      <p>
        <strong>HIPAA.</strong> Self-host inside your boundary. Do not send ePHI to a managed cloud you have not BAAd.
        Detectors flag SSN/email-like strings in completions — a safety net, not a DLP suite.
      </p>
      <p>
        <strong>SEC.</strong> The SEC pack is an internal evidence room: inventory, monitoring, change control via{" "}
        <span className="mono">prompt_version</span>. Not a filing.
      </p>

      <h2>Troubleshooting</h2>
      <ul>
        <li>Empty dashboard: wait for API startup seed, then hard-refresh the UI.</li>
        <li>401 on ingest: send header <span className="mono">X-API-Key: audit_demo_key</span>.</li>
        <li>CORS errors: UI must originate from localhost:5173 (see <span className="mono">CORS_ORIGINS</span>).</li>
      </ul>
      <p>
        Next: <Link to="/start">issue a trial key</Link> or <Link to="/app">open the dashboard</Link>.
      </p>
    </section>
  );
}
