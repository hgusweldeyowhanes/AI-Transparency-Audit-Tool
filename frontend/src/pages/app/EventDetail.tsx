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
              <MetricCard
                label="Groundedness"
                value={ev.groundedness_score != null ? ev.groundedness_score.toFixed(2) : "—"}
              />
            </div>
            <p>
              <Flags flags={ev.failure_flags} />
              <span className="muted">
                {" "}
                · prompt {ev.prompt_version} · {ev.provider}
                {ev.judge_rubric_version ? ` · rubric ${ev.judge_rubric_version}` : ""}
                {ev.purged_at ? " · redacted" : ""}
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
            {(ev.event_hash || ev.judge_scores) && (
              <article className="card" style={{ marginTop: 18 }}>
                <h3>Evidence</h3>
                {ev.event_hash && (
                  <p className="muted">
                    chain #{ev.chain_index} · hash {ev.event_hash.slice(0, 20)}… · prev{" "}
                    {(ev.prev_hash || "").slice(0, 12)}…
                  </p>
                )}
                {ev.judge_scores && Object.keys(ev.judge_scores).length > 0 && (
                  <pre className="block">{JSON.stringify(ev.judge_scores, null, 2)}</pre>
                )}
              </article>
            )}
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
