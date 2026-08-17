import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";
import { Sparkline } from "../../components/Charts";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .metrics(30)
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) {
    return (
      <div>
        <h1>Overview</h1>
        <p className="error">{err}</p>
        <p className="muted">Start the API on port 8000, then refresh.</p>
      </div>
    );
  }
  if (!data) return <p className="muted">Loading ledger…</p>;

  const series = (data.series || []).map((p: any) => p.events);
  const failSeries = (data.series || []).map((p: any) => p.failure_rate);

  return (
    <div>
      <div className="kicker">Last {data.days} days</div>
      <h1>Overview</h1>
      <div className="metrics">
        <div className="metric card">
          <div className="label">Events</div>
          <div className="value">{data.events.toLocaleString()}</div>
        </div>
        <div className="metric card">
          <div className="label">Failure rate</div>
          <div className="value">{(data.failure_rate * 100).toFixed(1)}%</div>
        </div>
        <div className="metric card">
          <div className="label">Spend</div>
          <div className="value">${data.total_cost_usd.toFixed(2)}</div>
        </div>
        <div className="metric card">
          <div className="label">Avg latency</div>
          <div className="value">{Math.round(data.avg_latency_ms)}ms</div>
        </div>
        <div className="metric card">
          <div className="label">Avg quality</div>
          <div className="value">{data.avg_quality.toFixed(2)}</div>
        </div>
      </div>
      <div className="grid-2" style={{ marginTop: 22 }}>
        <article className="card">
          <h3>Volume</h3>
          <Sparkline values={series} />
        </article>
        <article className="card">
          <h3>Failure rate</h3>
          <Sparkline values={failSeries} color="#fb7185" />
        </article>
      </div>
      <p style={{ marginTop: 22 }}>
        <Link to="/app/drift">Inspect drift incidents →</Link>
      </p>
    </div>
  );
}
