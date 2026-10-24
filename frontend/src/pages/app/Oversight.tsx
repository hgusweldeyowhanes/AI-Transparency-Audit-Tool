import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";
import { ReviewActions, useReviewer } from "../../components/ReviewActions";
import { Decision, Flags, MetricCard, PageState } from "../../components/Ui";
import { pct, when } from "../../format";
import { useApi } from "../../hooks/useApi";

const FILTERS = [
  ["pending", "Waiting"],
  ["reviewed", "Reviewed"],
  ["all", "All flagged"],
] as const;

export default function OversightPage() {
  const [status, setStatus] = useState<(typeof FILTERS)[number][0]>("pending");
  const [reviewer, setReviewer] = useReviewer();
  const { data, error, loading, reload } = useApi(() => api.oversight({ status, limit: 20 }), [status]);

  return (
    <div>
      <div className="kicker">EU AI Act Art. 14</div>
      <h1>Human oversight</h1>
      <p className="muted" style={{ maxWidth: 680 }}>
        Flagged model decisions wait here until a named person confirms the failure, marks the detector wrong, or
        escalates. The log is append-only, so a later review does not erase the earlier one.
      </p>
      <PageState error={error} loading={loading && !data} loadingText="Loading the review queue…">
        {data && (
          <>
            <div className="metrics">
              <MetricCard label="Waiting" value={data.stats.pending.toLocaleString()} />
              <MetricCard label="Coverage" value={pct(data.stats.coverage)} hint={`${data.stats.reviewed} reviewed`} />
              <MetricCard label="Confirmed" value={data.stats.confirmed.toLocaleString()} />
              <MetricCard label="False positives" value={data.stats.false_positive.toLocaleString()} />
            </div>

            <label style={{ marginTop: 22 }}>
              Reviewer
              <input
                value={reviewer}
                onChange={(e) => setReviewer(e.target.value)}
                style={{ display: "block", marginTop: 6, minWidth: 240 }}
              />
            </label>

            <div className="filters">
              {FILTERS.map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  className={id === status ? "btn btn-sm btn-primary" : "btn btn-sm btn-ghost"}
                  onClick={() => setStatus(id)}
                >
                  {label}
                </button>
              ))}
            </div>

            {data.queue.length === 0 ? (
              <p className="notice">
                {data.stats.flagged_events === 0
                  ? "No flagged events yet. Detectors will queue them here."
                  : status === "pending"
                    ? "Every flagged event has a human decision."
                    : "Nothing in this view."}
              </p>
            ) : (
              data.queue.map((item) => (
                <article className="card review-card" key={item.id}>
                  <div>
                    <Flags flags={item.failure_flags} />
                    <span className="muted">
                      {" "}
                      · {item.model} · prompt {item.prompt_version || "—"} · {when(item.timestamp)}
                    </span>
                  </div>
                  <p className="snippet">
                    <strong>Prompt. </strong>
                    {item.prompt || "(empty)"}
                  </p>
                  <p className="snippet">
                    <strong>Completion. </strong>
                    {item.completion || "(empty)"}
                  </p>
                  {item.review ? (
                    <p className="snippet">
                      Latest: <Decision decision={item.review.decision} /> by {item.review.reviewer}
                      {item.review.note ? ` — ${item.review.note}` : ""}
                    </p>
                  ) : null}
                  <ReviewActions eventId={item.id} reviewer={reviewer} flagged onDone={reload} />
                  <p style={{ margin: 0 }}>
                    <Link to={`/app/events/${item.id}`}>Open full trace</Link>
                  </p>
                </article>
              ))
            )}

            <h2 style={{ marginTop: 36 }}>Recent decisions</h2>
            {data.recent.length === 0 ? (
              <p className="muted">No decisions recorded yet.</p>
            ) : (
              <table className="data">
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Reviewer</th>
                    <th>Decision</th>
                    <th>Note</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent.map((review) => (
                    <tr key={review.id}>
                      <td>{when(review.created_at)}</td>
                      <td>{review.reviewer}</td>
                      <td>
                        <Decision decision={review.decision} />
                      </td>
                      <td>{review.note || "—"}</td>
                      <td>
                        <Link to={`/app/events/${review.event_id}`}>Trace</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </PageState>
    </div>
  );
}
