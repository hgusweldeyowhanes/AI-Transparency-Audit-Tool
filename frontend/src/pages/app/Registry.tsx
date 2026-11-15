import { useState } from "react";
import { api } from "../../api";
import { PageState } from "../../components/Ui";
import { useApi } from "../../hooks/useApi";

export default function RegistryPage() {
  const models = useApi(() => api.models(), []);
  const prompts = useApi(() => api.prompts(), []);
  const [statusNote, setStatusNote] = useState("");

  async function deprecatePrompt(version: string) {
    setStatusNote("");
    try {
      await api.savePrompt({ version, status: "deprecated" });
      setStatusNote(`Marked ${version} deprecated`);
      prompts.reload();
    } catch (err) {
      setStatusNote(err instanceof Error ? err.message : String(err));
    }
  }

  async function approvePrompt(version: string) {
    setStatusNote("");
    try {
      await api.savePrompt({ version, status: "approved" });
      setStatusNote(`Approved ${version}`);
      prompts.reload();
    } catch (err) {
      setStatusNote(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div>
      <div className="kicker">Change management</div>
      <h1>Model & prompt registry</h1>
      {statusNote && <p>{statusNote}</p>}
      <div className="grid-2" style={{ marginTop: 12 }}>
        <article className="card">
          <h3>Models</h3>
          <PageState error={models.error} loading={models.loading}>
            <table className="data">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Provider</th>
                  <th>Status</th>
                  <th>Owner</th>
                </tr>
              </thead>
              <tbody>
                {models.data?.models.map((m) => (
                  <tr key={m.id}>
                    <td>{m.name}</td>
                    <td>{m.provider}</td>
                    <td>{m.status}</td>
                    <td>{m.owner || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </PageState>
        </article>
        <article className="card">
          <h3>Prompt versions</h3>
          <PageState error={prompts.error} loading={prompts.loading}>
            {prompts.data?.prompts.map((p) => (
              <div key={p.id} style={{ marginBottom: 16, borderBottom: "1px solid var(--line)", paddingBottom: 12 }}>
                <strong>{p.version}</strong>
                <span className="muted">
                  {" "}
                  · {p.status} · {p.model || "any model"} · {p.owner || "unassigned"}
                </span>
                <pre className="block" style={{ maxHeight: 120, overflow: "auto" }}>
                  {p.content}
                </pre>
                <p className="muted">hash {p.content_hash?.slice(0, 16)}…</p>
                <div style={{ display: "flex", gap: 8 }}>
                  <button type="button" onClick={() => approvePrompt(p.version)}>
                    Approve
                  </button>
                  <button type="button" onClick={() => deprecatePrompt(p.version)}>
                    Deprecate
                  </button>
                </div>
              </div>
            ))}
          </PageState>
        </article>
      </div>
    </div>
  );
}
