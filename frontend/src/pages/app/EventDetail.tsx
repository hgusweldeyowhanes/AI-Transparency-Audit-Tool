import { Link, useParams } from "react-router-dom";
import { api } from "../../api";
import { ReviewActions, useReviewer } from "../../components/ReviewActions";
import { Decision, Flags, MetricCard, PageState } from "../../components/Ui";
import { usd, when } from "../../format";
import { useApi } from "../../hooks/useApi";

export default function EventDetail() {
  const { id } = useParams();
  const [reviewer, setReviewer] = useReviewer();
  const { data: ev, error, loading } = useApi(() => api.event(id || ""), [id]);
  const reviews = useApi(() => api.eventReviews(id || ""), [id]);

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
            <article className="card" style={{ marginTop: 18 }}>
              <h3>Human oversight</h3>
              <label>
                Reviewer
                <input
                  value={reviewer}
                  onChange={(e) => setReviewer(e.target.value)}
                  style={{ display: "block", marginTop: 6, minWidth: 240 }}
                />
              </label>
              <div style={{ marginTop: 12 }}>
                <ReviewActions
                  eventId={ev.id}
                  reviewer={reviewer}
                  flagged={ev.failure_flags.length > 0}
                  onDone={reviews.reload}
                />
              </div>
              {reviews.loading ? (
                <p className="muted">Loading decisions…</p>
              ) : reviews.error ? (
                <p className="error">{reviews.error}</p>
              ) : reviews.data && reviews.data.length > 0 ? (
                <table className="data" style={{ marginTop: 8 }}>
                  <thead>
                    <tr>
                      <th>When</th>
                      <th>Reviewer</th>
                      <th>Decision</th>
                      <th>Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviews.data.map((review) => (
                      <tr key={review.id}>
                        <td>{when(review.created_at)}</td>
                        <td>{review.reviewer}</td>
                        <td>
                          <Decision decision={review.decision} />
                        </td>
                        <td>{review.note || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="muted">No decision on this trace yet.</p>
              )}
            </article>
          </>
        )}
      </PageState>
    </div>
  );
}
