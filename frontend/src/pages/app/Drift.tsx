import { useEffect, useState } from "react";
import { Sparkline } from "../../components/Charts";
import { api } from "../../api";

export default function DriftPage() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .drift()
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) return <p className="error">{err}</p>;
  if (!data) return <p className="muted">Computing windows…</p>;

  const cur = data.current_window.stats;
  const prev = data.previous_window.stats;
  const deltas = data.deltas || {};
  const series = (data.series || []).map((p: any) => p.factual_error_rate);

  function delta(key: string) {
    const v = deltas[key];
    if (v === null || v === undefined) return "—";
    const cls = v > 0.02 ? "up" : v < -0.02 ? "down" : "";
    return <span className={`delta ${cls}`}>{(v * 100).toFixed(1)}%</span>;
  }

  return (
    <div>
      <h1>Drift</h1>
      <p className="muted">Last 7 days vs the prior 7. Factual-error series is the case-study signal.</p>
      <div className="metrics">
        <div className="metric card">
          <div className="label">Failure rate</div>
          <div className="value">{(cur.failure_rate * 100).toFixed(1)}%</div>
          <div>vs {(prev.failure_rate * 100).toFixed(1)}% {delta("failure_rate")}</div>
        </div>
        <div className="metric card">
          <div className="label">Avg latency</div>
          <div className="value">{Math.round(cur.avg_latency_ms)}ms</div>
          <div>{delta("avg_latency_ms")}</div>
        </div>
        <div className="metric card">
          <div className="label">Avg cost</div>
          <div className="value">${cur.avg_cost_usd.toFixed(4)}</div>
          <div>{delta("avg_cost_usd")}</div>
        </div>
        <div className="metric card">
          <div className="label">Quality</div>
          <div className="value">{cur.avg_quality.toFixed(2)}</div>
          <div>{delta("avg_quality")}</div>
        </div>
      </div>
      <article className="card" style={{ marginTop: 18 }}>
        <h3>Factual-error rate (30d)</h3>
        <Sparkline values={series} color="#fbbf24" />
      </article>
      <h2 style={{ marginTop: 28 }}>Incidents</h2>
      {(data.incidents || []).length === 0 && <p className="muted">No spikes above threshold in this seed window.</p>}
      <div className="grid-2">
        {(data.incidents || []).map((inc: any) => (
          <article className="card" key={inc.date + inc.title}>
            <div className="kicker">{inc.date}</div>
            <h3>{inc.title}</h3>
            <p className="muted">{inc.detail}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
