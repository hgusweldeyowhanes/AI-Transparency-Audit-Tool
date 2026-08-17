import { useState } from "react";
import { api, apiBase } from "../../api";

export default function ReportsPage() {
  const [kind, setKind] = useState<"eu-ai-act" | "sec">("eu-ai-act");
  const [json, setJson] = useState<any>(null);
  const [err, setErr] = useState("");

  async function load(next: "eu-ai-act" | "sec") {
    setKind(next);
    setErr("");
    try {
      setJson(await api.report(next, "json"));
    } catch (e) {
      setErr(String(e));
    }
  }

  return (
    <div>
      <h1>Reports</h1>
      <p className="notice">Templates for evidence rooms — not legal advice, not a certificate of conformity.</p>
      <div className="cta-row">
        <button className="btn btn-primary" onClick={() => load("eu-ai-act")}>
          EU AI Act pack
        </button>
        <button className="btn btn-ghost" onClick={() => load("sec")}>
          SEC pack
        </button>
        <a className="btn btn-gold" href={`${apiBase}/v1/reports/${kind}?format=html`} target="_blank" rel="noreferrer">
          Open HTML
        </a>
      </div>
      {err && <p className="error">{err}</p>}
      {json && (
        <article className="card" style={{ marginTop: 18 }}>
          <h3>{json.title}</h3>
          <p className="muted">{json.disclaimer}</p>
          <p>
            Events: {json.inventory?.event_count} · Retention: {json.inventory?.retention_days} days
          </p>
          <table className="data">
            <thead>
              <tr>
                <th>Model</th>
                <th>Provider</th>
                <th>Events</th>
                <th>Failure rate</th>
              </tr>
            </thead>
            <tbody>
              {(json.inventory?.models || []).map((m: any) => (
                <tr key={m.model}>
                  <td>{m.model}</td>
                  <td>{m.provider}</td>
                  <td>{m.events}</td>
                  <td>{(m.failure_rate * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      )}
    </div>
  );
}
