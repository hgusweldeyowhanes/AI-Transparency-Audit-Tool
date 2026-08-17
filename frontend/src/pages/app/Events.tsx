import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";
import { Flags, PageState } from "../../components/Ui";
import { when } from "../../format";
import { useApi } from "../../hooks/useApi";
import { FLAGS, MODELS } from "../../types";

export default function EventsPage() {
  const [q, setQ] = useState("");
  const [model, setModel] = useState("");
  const [flag, setFlag] = useState("");
  const [applied, setApplied] = useState({ q: "", model: "", flag: "" });
  const { data, error, loading } = useApi(
    () => api.events({ ...applied, limit: 50 }),
    [applied.q, applied.model, applied.flag]
  );

  return (
    <div>
      <h1>Events</h1>
      <p className="muted">{data?.total ?? 0} matching in this window</p>
      <form
        className="filters"
        onSubmit={(e) => {
          e.preventDefault();
          setApplied({ q, model, flag });
        }}
      >
        <input placeholder="Search prompt / completion" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          <option value="">All models</option>
          {MODELS.map((name) => (
            <option key={name}>{name}</option>
          ))}
        </select>
        <select value={flag} onChange={(e) => setFlag(e.target.value)}>
          <option value="">All flags</option>
          {FLAGS.map((name) => (
            <option key={name}>{name}</option>
          ))}
        </select>
        <button className="btn btn-primary" type="submit">
          Search
        </button>
      </form>
      <PageState error={error} loading={loading} loadingText="Loading events…">
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
            {(data?.events ?? []).map((row) => (
              <tr key={row.id}>
                <td className="mono">{when(row.timestamp)}</td>
                <td>{row.model}</td>
                <td>{row.prompt_version}</td>
                <td>
                  <Flags flags={row.failure_flags} />
                </td>
                <td>{row.quality_score.toFixed(2)}</td>
                <td>
                  <Link to={`/app/events/${row.id}`}>Open</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </PageState>
    </div>
  );
}
