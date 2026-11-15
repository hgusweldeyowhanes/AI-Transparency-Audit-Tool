import { useState } from "react";
import { api } from "../../api";
import { PageState } from "../../components/Ui";
import { when } from "../../format";
import { useApi } from "../../hooks/useApi";

export default function IncidentsPage() {
  const { data, error, loading, reload } = useApi(() => api.incidents(), []);
  const [title, setTitle] = useState("");
  const [detail, setDetail] = useState("");
  const [busy, setBusy] = useState(false);

  async function create() {
    if (!title.trim()) return;
    setBusy(true);
    try {
      await api.createIncident({ title, detail, severity: "medium", status: "open" });
      setTitle("");
      setDetail("");
      reload();
    } finally {
      setBusy(false);
    }
  }

  async function setStatus(id: string, status: string) {
    await api.patchIncident(id, { status });
    reload();
  }

  return (
    <div>
      <div className="kicker">Incident workflow</div>
      <h1>Incidents</h1>
      <article className="card">
        <h3>Open an incident</h3>
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} style={{ display: "block", width: "100%", marginTop: 6 }} />
        </label>
        <label style={{ display: "block", marginTop: 10 }}>
          Detail
          <textarea value={detail} onChange={(e) => setDetail(e.target.value)} rows={3} style={{ display: "block", width: "100%", marginTop: 6 }} />
        </label>
        <button type="button" disabled={busy} onClick={create} style={{ marginTop: 10 }}>
          Create
        </button>
      </article>
      <PageState error={error} loading={loading}>
        <div style={{ marginTop: 18 }}>
          {data?.incidents.map((inc) => (
            <article key={inc.id} className="card" style={{ marginBottom: 14 }}>
              <h3>
                {inc.title}{" "}
                <span className="muted">
                  · {inc.severity} · {inc.status}
                </span>
              </h3>
              <p className="muted">
                Owner {inc.owner}
                {inc.prompt_version ? ` · prompt ${inc.prompt_version}` : ""}
                {inc.metric ? ` · metric ${inc.metric}` : ""} · updated {when(inc.updated_at)}
              </p>
              <p>{inc.detail}</p>
              {inc.rca && (
                <>
                  <h4>RCA</h4>
                  <p>{inc.rca}</p>
                </>
              )}
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button type="button" onClick={() => setStatus(inc.id, "investigating")}>
                  Investigating
                </button>
                <button type="button" onClick={() => setStatus(inc.id, "resolved")}>
                  Resolve
                </button>
                <button type="button" onClick={() => setStatus(inc.id, "dismissed")}>
                  Dismiss
                </button>
              </div>
            </article>
          ))}
        </div>
      </PageState>
    </div>
  );
}
