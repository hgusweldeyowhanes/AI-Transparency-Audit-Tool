from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import AuditEvent
from .ingest import loads_list


def _window(days=7, offset_days=0):
    end = datetime.utcnow() - timedelta(days=offset_days)
    start = end - timedelta(days=days)
    return start, end


def _agg(db: Session, start, end):
    q = db.query(AuditEvent).filter(AuditEvent.timestamp >= start, AuditEvent.timestamp < end)
    rows = q.all()
    n = len(rows)
    if n == 0:
        return {
            "events": 0,
            "failure_rate": 0.0,
            "avg_latency_ms": 0.0,
            "avg_cost_usd": 0.0,
            "avg_output_tokens": 0.0,
            "avg_quality": 0.0,
            "failed": 0,
        }
    failed = 0
    lat = cost = toks = qual = 0.0
    for r in rows:
        flags = loads_list(r.failure_flags)
        if flags:
            failed += 1
        lat += r.latency_ms or 0
        cost += r.cost_usd or 0
        toks += r.completion_tokens or 0
        qual += r.quality_score or 0
    return {
        "events": n,
        "failed": failed,
        "failure_rate": round(failed / float(n), 4),
        "avg_latency_ms": round(lat / n, 1),
        "avg_cost_usd": round(cost / n, 6),
        "avg_output_tokens": round(toks / float(n), 1),
        "avg_quality": round(qual / n, 3),
    }


def _delta(current, previous, key):
    a = current.get(key) or 0
    b = previous.get(key) or 0
    if b == 0:
        return None if a == 0 else 1.0
    return round((a - b) / float(b), 4)


def daily_series(db: Session, days=30):
    start = datetime.utcnow() - timedelta(days=days)
    rows = db.query(AuditEvent).filter(AuditEvent.timestamp >= start).order_by(AuditEvent.timestamp).all()
    buckets = {}  # type: Dict[str, Dict[str, Any]]
    for r in rows:
        day = r.timestamp.strftime("%Y-%m-%d")
        b = buckets.setdefault(
            day,
            {"date": day, "events": 0, "failed": 0, "cost_usd": 0.0, "latency_ms": 0.0, "factual_errors": 0},
        )
        b["events"] += 1
        flags = loads_list(r.failure_flags)
        if flags:
            b["failed"] += 1
        if "factual_error" in flags:
            b["factual_errors"] += 1
        b["cost_usd"] += r.cost_usd or 0
        b["latency_ms"] += r.latency_ms or 0
    series = []
    for i in range(days, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        b = buckets.get(d, {"date": d, "events": 0, "failed": 0, "cost_usd": 0.0, "latency_ms": 0.0, "factual_errors": 0})
        n = b["events"] or 1
        series.append(
            {
                "date": d,
                "events": b["events"],
                "failure_rate": round(b["failed"] / float(b["events"]), 4) if b["events"] else 0,
                "factual_error_rate": round(b["factual_errors"] / float(b["events"]), 4) if b["events"] else 0,
                "cost_usd": round(b["cost_usd"], 4),
                "avg_latency_ms": round(b["latency_ms"] / n, 1) if b["events"] else 0,
            }
        )
    return series


def detect_incidents(series):
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
    # Keep the strongest / first cluster
    if len(incidents) > 3:
        incidents = incidents[:3]
    return incidents


def compute_drift(db: Session):
    cur_start, cur_end = _window(7, 0)
    prev_start, prev_end = _window(7, 7)
    current = _agg(db, cur_start, cur_end)
    previous = _agg(db, prev_start, prev_end)
    series = daily_series(db, 30)
    return {
        "current_window": {"start": cur_start.isoformat() + "Z", "end": cur_end.isoformat() + "Z", "stats": current},
        "previous_window": {"start": prev_start.isoformat() + "Z", "end": prev_end.isoformat() + "Z", "stats": previous},
        "deltas": {
            "failure_rate": _delta(current, previous, "failure_rate"),
            "avg_latency_ms": _delta(current, previous, "avg_latency_ms"),
            "avg_cost_usd": _delta(current, previous, "avg_cost_usd"),
            "avg_output_tokens": _delta(current, previous, "avg_output_tokens"),
            "avg_quality": _delta(current, previous, "avg_quality"),
        },
        "series": series,
        "incidents": detect_incidents(series),
    }
