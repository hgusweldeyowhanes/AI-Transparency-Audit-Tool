from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ..models import AuditEvent
from .ingest import loads_list


def compare_models(db: Session, days=30):
    start = datetime.utcnow() - timedelta(days=days)
    rows = db.query(AuditEvent).filter(AuditEvent.timestamp >= start).all()
    by_model = defaultdict(
        lambda: {
            "model": "",
            "provider": "",
            "events": 0,
            "failed": 0,
            "cost_usd": 0.0,
            "latency_ms": 0.0,
            "quality": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }
    )
    for r in rows:
        b = by_model[r.model]
        b["model"] = r.model
        b["provider"] = r.provider
        b["events"] += 1
        if loads_list(r.failure_flags):
            b["failed"] += 1
        b["cost_usd"] += r.cost_usd or 0
        b["latency_ms"] += r.latency_ms or 0
        b["quality"] += r.quality_score or 0
        b["prompt_tokens"] += r.prompt_tokens or 0
        b["completion_tokens"] += r.completion_tokens or 0

    models = []
    for b in by_model.values():
        n = b["events"] or 1
        models.append(
            {
                "model": b["model"],
                "provider": b["provider"],
                "events": b["events"],
                "failure_rate": round(b["failed"] / float(b["events"]), 4) if b["events"] else 0,
                "total_cost_usd": round(b["cost_usd"], 4),
                "avg_cost_usd": round(b["cost_usd"] / n, 6),
                "avg_latency_ms": round(b["latency_ms"] / n, 1),
                "avg_quality": round(b["quality"] / n, 3),
                "cost_per_quality": round((b["cost_usd"] / n) / max(b["quality"] / n, 0.05), 6),
                "prompt_tokens": b["prompt_tokens"],
                "completion_tokens": b["completion_tokens"],
            }
        )
    models.sort(key=lambda m: m["cost_per_quality"])
    return {"days": days, "models": models}
