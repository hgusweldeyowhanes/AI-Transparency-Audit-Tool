import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, AuditEvent } from "../../api";

export default function EventsPage() {
  const [q, setQ] = useState("");
  const [model, setModel] = useState("");
  const [flag, setFlag] = useState("");
  const [rows, setRows] = useState<AuditEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [err, setErr] = useState("");

  function load() {
    setErr("");
    api
      .events({ q, model, flag, limit: 50 })
      .then((d) => {
        setRows(d.events);
        setTotal(d.total);
      })
      .catch((e) => setErr(String(e)));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <h1>Events</h1>
      <p className="muted">{total} matching in this window</p>
      <div className="filters">
        <input placeholder="Search prompt / completion" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          <option value="">All models</option>
          <option>gpt-4o</option>
          <option>claude-3-5-sonnet</option>
          <option>llama-3.1-70b</option>
        </select>
        <select value={flag} onChange={(e) => setFlag(e.target.value)}>
          <option value="">All flags</option>
          <option>factual_error</option>
          <option>empty</option>
          <option>refusal</option>
          <option>knowledge_gap</option>
          <option>hedging</option>
          <option>pii_leak</option>
          <option>latency_anomaly</option>
        </select>
        <button className="btn btn-primary" onClick={load}>
          Search
        </button>
      </div>
      {err && <p className="error">{err}</p>}
      <table className="data">
        <thead>
          <tr>
            <th>When</th>
            <th>Model</th>
            <th>Version</th>
            <th>Flags</th>
            <th>Quality</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((e) => (
            <tr key={e.id}>
              <td className="mono">{new Date(e.timestamp).toISOString().slice(0, 16).replace("T", " ")}</td>
              <td>{e.model}</td>
              <td>{e.prompt_version}</td>
              <td>
                {e.failure_flags.length
                  ? e.failure_flags.map((f) => (
                      <span className="flag" key={f}>
                        {f}
                      </span>
                    ))
                  : <span className="flag ok-pill">clean</span>}
              </td>
              <td>{e.quality_score.toFixed(2)}</td>
              <td>
                <Link to={`/app/events/${e.id}`}>Open</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
