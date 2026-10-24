import { useState } from "react";
import { api } from "../api";
import { ReviewDecision } from "../types";

const ACTIONS: { id: ReviewDecision; label: string; className: string; flaggedOnly?: boolean }[] = [
  { id: "confirmed", label: "Confirm failure", className: "btn btn-sm btn-gold", flaggedOnly: true },
  { id: "false_positive", label: "False positive", className: "btn btn-sm btn-primary", flaggedOnly: true },
  { id: "escalated", label: "Escalate", className: "btn btn-sm btn-ghost", flaggedOnly: true },
  { id: "cleared", label: "Mark reviewed", className: "btn btn-sm btn-primary" },
];

export function useReviewer() {
  const [reviewer, setReviewer] = useState(() => localStorage.getItem("audit_reviewer") || "operator");

  function update(value: string) {
    setReviewer(value);
    localStorage.setItem("audit_reviewer", value);
  }

  return [reviewer, update] as const;
}

export function ReviewActions({
  eventId,
  reviewer,
  flagged,
  onDone,
}: {
  eventId: string;
  reviewer: string;
  flagged: boolean;
  onDone: () => void;
}) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(decision: ReviewDecision) {
    const name = reviewer.trim();
    if (!name) {
      setError("Add your name so the decision is attributable.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api.review({ event_id: eventId, reviewer: name, decision, note: note.trim() });
      setNote("");
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  const actions = ACTIONS.filter((action) => (flagged ? action.id !== "cleared" : !action.flaggedOnly));

  return (
    <div className="review-actions">
      <textarea
        className="review-note"
        placeholder="Why this decision? Optional, but it is what an auditor will read."
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      <div className="queue-actions">
        {actions.map((action) => (
          <button
            key={action.id}
            type="button"
            className={action.className}
            disabled={busy}
            onClick={() => submit(action.id)}
          >
            {action.label}
          </button>
        ))}
      </div>
      {error ? <p className="error">{error}</p> : null}
    </div>
  );
}
