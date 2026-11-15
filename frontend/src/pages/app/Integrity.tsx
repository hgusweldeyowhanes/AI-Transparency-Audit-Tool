import { useState } from "react";
import { api } from "../../api";
import { MetricCard, PageState } from "../../components/Ui";
import { useApi } from "../../hooks/useApi";

export default function IntegrityPage() {
  const { data, error, loading, reload } = useApi(() => api.integrity(), []);
  const rubrics = useApi(() => api.rubrics(), []);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  async function runRetention() {
    setBusy(true);
    setNote("");
    try {
      const result = await api.retention();
      setNote(`Purged ${result.purged} events. ${result.note}`);
      reload();
    } catch (err) {
      setNote(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="kicker">Evidence integrity</div>
      <h1>Hash chain & retention</h1>
      <PageState error={error} loading={loading}>
        {data && (
          <>
            <div className="metrics">
              <MetricCard label="Chain OK" value={data.ok ? "yes" : "BROKEN"} />
              <MetricCard label="Checked" value={data.checked.toLocaleString()} />
              <MetricCard label="Redacted" value={String(data.redacted ?? 0)} />
              <MetricCard label="Tip index" value={String(data.tip_index)} />
            </div>
            <article className="card" style={{ marginTop: 18 }}>
              <h3>Tip hash</h3>
              <pre className="block">{data.tip_hash}</pre>
              {data.broken_at && (
                <p className="error" style={{ marginTop: 12 }}>
                  Break: {JSON.stringify(data.broken_at)}
                </p>
              )}
              <p className="muted">
                Each ingest seals <code>event_hash = sha256(prev_hash + canonical payload)</code>. Soft retention
                redacts prompt/completion but keeps the original digest for audit.
              </p>
              <button type="button" disabled={busy} onClick={runRetention} style={{ marginTop: 12 }}>
                {busy ? "Running…" : "Run retention purge"}
              </button>
              {note && <p style={{ marginTop: 10 }}>{note}</p>}
            </article>
          </>
        )}
      </PageState>
      <article className="card" style={{ marginTop: 18 }}>
        <h3>Active rubrics</h3>
        <PageState error={rubrics.error} loading={rubrics.loading}>
          {rubrics.data?.rubrics.map((r) => (
            <div key={r.id} style={{ marginBottom: 14 }}>
              <strong>
                {r.name} · v{r.version}
              </strong>
              {r.active ? <span className="muted"> · active</span> : null}
              <p className="muted">{r.description}</p>
              <ul>
                {r.rules.map((rule) => (
                  <li key={rule}>{rule}</li>
                ))}
              </ul>
              <p className="muted">min groundedness {r.min_groundedness}</p>
            </div>
          ))}
        </PageState>
      </article>
    </div>
  );
}
