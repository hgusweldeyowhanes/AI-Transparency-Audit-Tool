import { Link } from "react-router-dom";
import { api } from "../../api";
import { Sparkline } from "../../components/Charts";
import { MetricCard, PageState } from "../../components/Ui";
import { pct, usd } from "../../format";
import { useApi } from "../../hooks/useApi";

export default function Dashboard() {
  const { data, error, loading } = useApi(() => api.metrics(30), []);

  return (
    <div>
      <div className="kicker">Last {data?.days ?? 30} days</div>
      <h1>Overview</h1>
      <PageState error={error} loading={loading} loadingText="Loading ledger…">
        {data && (
          <>
            <div className="metrics">
              <MetricCard label="Events" value={data.events.toLocaleString()} />
              <MetricCard label="Failure rate" value={pct(data.failure_rate)} />
              <MetricCard label="Spend" value={usd(data.total_cost_usd)} />
              <MetricCard label="Avg latency" value={`${Math.round(data.avg_latency_ms)}ms`} />
              <MetricCard label="Avg quality" value={data.avg_quality.toFixed(2)} />
            </div>
            <div className="grid-2" style={{ marginTop: 22 }}>
              <article className="card">
                <h3>Volume</h3>
                <Sparkline values={data.series.map((p) => p.events)} />
              </article>
              <article className="card">
                <h3>Failure rate</h3>
                <Sparkline values={data.series.map((p) => p.failure_rate)} color="#fb7185" />
              </article>
            </div>
            <p style={{ marginTop: 22 }}>
              <Link to="/app/drift">Inspect drift incidents →</Link>
            </p>
          </>
        )}
      </PageState>
    </div>
  );
}
