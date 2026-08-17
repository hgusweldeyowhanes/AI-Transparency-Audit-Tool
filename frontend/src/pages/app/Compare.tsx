import { useEffect, useState } from "react";
import { Bar } from "../../components/Charts";
import { api } from "../../api";

export default function ComparePage() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .compare(30)
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) return <p className="error">{err}</p>;
  if (!data) return <p className="muted">Ranking models…</p>;

  const models = data.models || [];
  const maxCost = Math.max(...models.map((m: any) => m.avg_cost_usd), 0.000001);
  const maxFail = Math.max(...models.map((m: any) => m.failure_rate), 0.000001);

  return (
    <div>
      <h1>Compare</h1>
      <p className="muted">Lower cost-per-quality is better. Ranked on your traffic, not a public leaderboard.</p>
      <article className="card">
        <h3>Average cost / call</h3>
        {models.map((m: any) => (
          <Bar key={m.model} label={m.model} value={Number(m.avg_cost_usd.toFixed(5))} max={maxCost} suffix="" />
        ))}
      </article>
      <article className="card" style={{ marginTop: 16 }}>
        <h3>Failure rate</h3>
        {models.map((m: any) => (
          <Bar key={m.model} label={m.model} value={Number((m.failure_rate * 100).toFixed(2))} max={maxFail * 100} suffix="%" />
        ))}
      </article>
      <table className="data" style={{ marginTop: 18 }}>
        <thead>
          <tr>
            <th>Model</th>
            <th>Provider</th>
            <th>Events</th>
            <th>Avg quality</th>
            <th>Cost / quality</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {models.map((m: any) => (
            <tr key={m.model}>
              <td>{m.model}</td>
              <td>{m.provider}</td>
              <td>{m.events}</td>
              <td>{m.avg_quality.toFixed(3)}</td>
              <td className="mono">{m.cost_per_quality.toFixed(6)}</td>
              <td>{Math.round(m.avg_latency_ms)}ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
