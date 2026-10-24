import uuid

from ..clock import utc_now
from ..models import OversightReview
from ..repositories import EventStore, ReviewStore

DECISION_KEYS = ("confirmed", "false_positive", "escalated", "cleared")


def _clip(text, limit=220):
    flat = " ".join((text or "").split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1].rstrip() + "…"


def _latest_by_event(reviews):
    latest = {}
    for review in reviews:
        if review.event_id not in latest:
            latest[review.event_id] = review
    return latest


def _stats(flagged, latest):
    counts = {key: 0 for key in DECISION_KEYS}
    for event in flagged:
        review = latest.get(event.id)
        if review and review.decision in counts:
            counts[review.decision] += 1
    reviewed = sum(counts.values())
    total = len(flagged)
    return {
        "flagged_events": total,
        "reviewed": reviewed,
        "pending": total - reviewed,
        "coverage": (float(reviewed) / total) if total else 0.0,
        "confirmed": counts["confirmed"],
        "false_positive": counts["false_positive"],
        "escalated": counts["escalated"],
        "cleared": counts["cleared"],
    }


def _queue_item(event, review):
    return {
        "id": event.id,
        "timestamp": event.timestamp,
        "model": event.model,
        "prompt_version": event.prompt_version,
        "failure_flags": event.flags,
        "quality_score": event.quality_score,
        "prompt": _clip(event.prompt),
        "completion": _clip(event.completion),
        "review": review.to_dict() if review else None,
    }


def build_oversight(db, status="pending", limit=30):
    reviews = ReviewStore(db).newest_first()
    latest = _latest_by_event(reviews)
    flagged = sorted(
        (row for row in EventStore(db).all() if row.failed),
        key=lambda row: row.timestamp,
        reverse=True,
    )
    if status == "pending":
        chosen = [row for row in flagged if row.id not in latest]
    elif status == "reviewed":
        chosen = [row for row in flagged if row.id in latest]
    else:
        chosen = flagged
    return {
        "stats": _stats(flagged, latest),
        "queue": [_queue_item(row, latest.get(row.id)) for row in chosen[:limit]],
        "recent": [review.to_dict() for review in reviews[:12]],
    }


def oversight_summary(db):
    return build_oversight(db, status="pending", limit=1)["stats"]


def oversight_article(stats):
    if not stats["flagged_events"]:
        return (
            "Flagged model outputs are queued for a named human decision "
            "(confirm, false positive, escalate, or clear). None are flagged in this ledger yet."
        )
    return (
        "Append-only human decisions on flagged outputs: {reviewed} of {flagged} reviewed "
        "({coverage:.0%} coverage). Confirm, false positive, escalate, or clear."
    ).format(
        reviewed=stats["reviewed"],
        flagged=stats["flagged_events"],
        coverage=stats["coverage"],
    )


def add_review(db, payload):
    if not EventStore(db).get(payload.event_id):
        return None
    row = OversightReview(
        id=str(uuid.uuid4()),
        event_id=payload.event_id,
        created_at=utc_now(),
        reviewer=payload.reviewer,
        decision=payload.decision,
        note=payload.note or "",
    )
    db.add(row)
    return row


def reviews_for(db, event_id):
    if not EventStore(db).get(event_id):
        return None
    return [row.to_dict() for row in ReviewStore(db).for_event(event_id)]
