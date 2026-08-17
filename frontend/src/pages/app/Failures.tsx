import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";

export default function FailuresPage() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .failures()
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) return <p className="error">{err}</p>;
  if (!data) return <p className="muted">Clustering…</p>;

  return (
    <div>
      <h1>Failures</h1>
      <p className="muted">
        Scanned {data.scanned} events · {data.failed_events} with at least one flag
      </p>
      <div className="grid-2">
        {(data.taxonomy || []).map((t: any) => (
          <div key={t.flag} className="card">
            <div className="kicker">{t.flag}</div>
            <h3>{t.label}</h3>
            <div className="value" style={{ fontFamily: "var(--serif)", fontSize: 28 }}>
              {t.count}
            </div>
          </div>
        ))}
      </div>
      <h2 style={{ marginTop: 32 }}>Clusters</h2>
      <table className="data">
        <thead>
          <tr>
            <th>Flag</th>
            <th>Count</th>
            <th>Sample</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {(data.clusters || []).map((c: any, i: number) => (
            <tr key={i}>
              <td>
                <span className="flag">{c.flag}</span>
              </td>
              <td>{c.count}</td>
              <td>{c.sample}</td>
              <td>
                {c.event_ids?.[0] ? <Link to={`/app/events/${c.event_ids[0]}`}>Example</Link> : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
