import { Link, useParams } from "react-router-dom";
import { api } from "../../api";
import { Flags, MetricCard, PageState } from "../../components/Ui";
import { usd } from "../../format";
import { useApi } from "../../hooks/useApi";

export default function EventDetail() {
  const { id } = useParams();
  const { data: ev, error, loading } = useApi(() => api.event(id || ""), [id]);

  return (
    <div>
      <p>
        <Link to="/app/events">← Events</Link>
      </p>
      <PageState error={error} loading={loading}>
        {ev && (
          <>
            <h1>Trace {ev.trace_id.slice(0, 8)}</h1>
            <div className="metrics">
              <MetricCard label="Model" value={<span style={{ fontSize: 22 }}>{ev.model}</span>} />
              <MetricCard label="Latency" value={`${ev.latency_ms}ms`} />
              <MetricCard label="Cost" value={usd(ev.cost_usd, 4)} />
              <MetricCard label="Quality" value={ev.quality_score.toFixed(2)} />
            </div>
            <p>
              <Flags flags={ev.failure_flags} />
              <span className="muted">
                {" "}
                · prompt {ev.prompt_version} · {ev.provider}
              </span>
            </p>
            <div className="grid-2">
              <article className="card">
                <h3>Prompt</h3>
                <pre className="block">{ev.prompt}</pre>
              </article>
              <article className="card">
                <h3>Completion</h3>
                <pre className="block">{ev.completion || "(empty)"}</pre>
              </article>
            </div>
          </>
        )}
      </PageState>
    </div>
  );
}
