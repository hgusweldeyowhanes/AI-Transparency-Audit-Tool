from sqlalchemy.orm import Session

from ..clock import iso_z
from ..repositories import EventStore
from .analytics import daily_series, relative_delta, summarize, window_bounds


def detect_incidents(series, max_incidents=3):
    incidents = []
    for i, point in enumerate(series):
        if i < 3:
            continue
        prior = series[i - 3 : i]
        avg = sum(p["factual_error_rate"] for p in prior) / 3.0
        if point["factual_error_rate"] >= 0.025 and point["factual_error_rate"] > avg + 0.015:
            incidents.append(
                {
                    "date": point["date"],
                    "title": "Factual-error rate spike",
                    "detail": (
                        "Factual-error rate rose to {:.1%} (prior 3-day average {:.1%}). "
                        "This pattern matches an aggressive prompt-version change."
                    ).format(point["factual_error_rate"], avg),
                    "metric": "factual_error_rate",
                    "value": point["factual_error_rate"],
                }
            )
        if len(incidents) >= max_incidents:
            break
    return incidents


def compute_drift(db, window_days=7, series_days=30):
    store = EventStore(db)
    cur_start, cur_end = window_bounds(window_days, 0)
    prev_start, prev_end = window_bounds(window_days, window_days)
    current = summarize(store.between(cur_start, cur_end))
    previous = summarize(store.between(prev_start, prev_end))
    series = daily_series(store.since(window_bounds(series_days, 0)[0]), days=series_days)
    keys = ("failure_rate", "avg_latency_ms", "avg_cost_usd", "avg_output_tokens", "avg_quality")
    return {
        "current_window": {"start": iso_z(cur_start), "end": iso_z(cur_end), "stats": current},
        "previous_window": {"start": iso_z(prev_start), "end": iso_z(prev_end), "stats": previous},
        "deltas": {key: relative_delta(current, previous, key) for key in keys},
        "series": series,
        "incidents": detect_incidents(series),
    }


def compute_metrics(db, days=30):
    store = EventStore(db)
    start, _end = window_bounds(days, 0)
    rows = store.since(start)
    stats = summarize(rows)
    return {
        "days": days,
        "events": stats["events"],
        "failed_events": stats["failed"],
        "failure_rate": stats["failure_rate"],
        "total_cost_usd": stats["total_cost_usd"],
        "avg_latency_ms": stats["avg_latency_ms"],
        "avg_quality": stats["avg_quality"],
        "series": daily_series(rows, days=days),
    }
