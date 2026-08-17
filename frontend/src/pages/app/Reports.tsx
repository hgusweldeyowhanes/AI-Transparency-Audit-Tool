import { useState } from "react";
import { api, apiBase } from "../../api";
import { PageState } from "../../components/Ui";
import { pct } from "../../format";
import { useApi } from "../../hooks/useApi";

export default function ReportsPage() {
  const [kind, setKind] = useState<"eu-ai-act" | "sec">("eu-ai-act");
  const { data, error, loading } = useApi(() => api.report(kind), [kind]);

  return (
    <div>
      <h1>Reports</h1>
      <p className="notice">Templates for evidence rooms — not legal advice, not a certificate of conformity.</p>
      <div className="cta-row">
        <button className="btn btn-primary" onClick={() => setKind("eu-ai-act")}>
          EU AI Act pack
        </button>
        <button className="btn btn-ghost" onClick={() => setKind("sec")}>
          SEC pack
        </button>
        <a className="btn btn-gold" href={`${apiBase}/v1/reports/${kind}?format=html`} target="_blank" rel="noreferrer">
          Open HTML
        </a>
      </div>
      <PageState error={error} loading={loading && !data}>
        {data && (
          <article className="card" style={{ marginTop: 18 }}>
            <h3>{data.title}</h3>
            <p className="muted">{data.disclaimer}</p>
            <p>
              Events: {data.inventory.event_count} · Retention: {data.inventory.retention_days} days
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
                {data.inventory.models.map((m) => (
                  <tr key={m.model}>
                    <td>{m.model}</td>
                    <td>{m.provider}</td>
                    <td>{m.events}</td>
                    <td>{pct(m.failure_rate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        )}
      </PageState>
    </div>
  );
}
