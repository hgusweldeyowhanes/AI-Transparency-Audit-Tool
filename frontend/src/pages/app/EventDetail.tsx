import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, AuditEvent } from "../../api";

export default function EventDetail() {
  const { id } = useParams();
  const [ev, setEv] = useState<AuditEvent | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!id) return;
    api
      .event(id)
      .then(setEv)
      .catch((e) => setErr(String(e)));
  }, [id]);

  if (err) return <p className="error">{err}</p>;
  if (!ev) return <p className="muted">Loading…</p>;

  return (
    <div>
      <p>
        <Link to="/app/events">← Events</Link>
      </p>
      <h1>Trace {ev.trace_id.slice(0, 8)}</h1>
      <div className="metrics">
        <div className="metric card">
          <div className="label">Model</div>
          <div className="value" style={{ fontSize: 22 }}>
            {ev.model}
          </div>
        </div>
        <div className="metric card">
          <div className="label">Latency</div>
          <div className="value">{ev.latency_ms}ms</div>
        </div>
        <div className="metric card">
          <div className="label">Cost</div>
          <div className="value">${ev.cost_usd.toFixed(4)}</div>
        </div>
        <div className="metric card">
          <div className="label">Quality</div>
          <div className="value">{ev.quality_score.toFixed(2)}</div>
        </div>
      </div>
      <p>
        {ev.failure_flags.map((f) => (
          <span className="flag" key={f}>
            {f}
          </span>
        ))}
        <span className="muted"> · prompt {ev.prompt_version} · {ev.provider}</span>
      </p>
      <div className="grid-2">
        <article className="card">
          <h3>Prompt</h3>
          <pre className="block">{ev.prompt}</pre>
        </article>
        <article className="card">
          <h3>Completion</h3>
          <pre className="block">{ev.completion || "(empty)"}</pre>
        </article>
      </div>
    </div>
  );
}
