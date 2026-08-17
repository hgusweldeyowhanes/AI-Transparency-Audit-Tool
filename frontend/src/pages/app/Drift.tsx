import { Sparkline } from "../../components/Charts";
import { MetricCard, PageState } from "../../components/Ui";
import { deltaClass, pct, usd } from "../../format";
import { useApi } from "../../hooks/useApi";
import { api } from "../../api";

export default function DriftPage() {
  const { data, error, loading } = useApi(() => api.drift(), []);

  function delta(key: string) {
    const value = data?.deltas?.[key];
    if (value == null) return "—";
    return <span className={`delta ${deltaClass(value)}`}>{pct(value)}</span>;
  }

  const cur = data?.current_window.stats;
  const prev = data?.previous_window.stats;

  return (
    <div>
      <h1>Drift</h1>
      <p className="muted">Last 7 days vs the prior 7. Factual-error series is the case-study signal.</p>
      <PageState error={error} loading={loading} loadingText="Computing windows…">
        {data && cur && prev && (
          <>
            <div className="metrics">
              <MetricCard
                label="Failure rate"
                value={pct(cur.failure_rate)}
                hint={
                  <>
                    vs {pct(prev.failure_rate)} {delta("failure_rate")}
                  </>
                }
              />
              <MetricCard label="Avg latency" value={`${Math.round(cur.avg_latency_ms)}ms`} hint={delta("avg_latency_ms")} />
              <MetricCard label="Avg cost" value={usd(cur.avg_cost_usd, 4)} hint={delta("avg_cost_usd")} />
              <MetricCard label="Quality" value={cur.avg_quality.toFixed(2)} hint={delta("avg_quality")} />
            </div>
            <article className="card" style={{ marginTop: 18 }}>
              <h3>Factual-error rate (30d)</h3>
              <Sparkline values={data.series.map((p) => p.factual_error_rate || 0)} color="#fbbf24" />
            </article>
            <h2 style={{ marginTop: 28 }}>Incidents</h2>
            {data.incidents.length === 0 && <p className="muted">No spikes above threshold in this seed window.</p>}
            <div className="grid-2">
              {data.incidents.map((inc) => (
                <article className="card" key={inc.date + inc.title}>
                  <div className="kicker">{inc.date}</div>
                  <h3>{inc.title}</h3>
                  <p className="muted">{inc.detail}</p>
                </article>
              ))}
            </div>
          </>
        )}
      </PageState>
    </div>
  );
}
