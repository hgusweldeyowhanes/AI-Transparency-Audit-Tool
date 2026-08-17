from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditEvent
from ..services.ingest import loads_list

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])


@router.get("")
def metrics(db: Session = Depends(get_db), days: int = Query(30, ge=1, le=365)):
    start = datetime.utcnow() - timedelta(days=days)
    rows = db.query(AuditEvent).filter(AuditEvent.timestamp >= start).all()
    n = len(rows)
    failed = 0
    cost = latency = quality = 0.0
    by_day = {}
    for r in rows:
        flags = loads_list(r.failure_flags)
        if flags:
            failed += 1
        cost += r.cost_usd or 0
        latency += r.latency_ms or 0
        quality += r.quality_score or 0
        day = r.timestamp.strftime("%Y-%m-%d")
        b = by_day.setdefault(day, {"date": day, "events": 0, "failed": 0, "cost_usd": 0.0})
        b["events"] += 1
        if flags:
            b["failed"] += 1
        b["cost_usd"] += r.cost_usd or 0

    series = []
    for i in range(days, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        b = by_day.get(d, {"date": d, "events": 0, "failed": 0, "cost_usd": 0.0})
        series.append(
            {
                "date": d,
                "events": b["events"],
                "failure_rate": round(b["failed"] / float(b["events"]), 4) if b["events"] else 0,
                "cost_usd": round(b["cost_usd"], 4),
            }
        )

    return {
        "days": days,
        "events": n,
        "failed_events": failed,
        "failure_rate": round(failed / float(n), 4) if n else 0,
        "total_cost_usd": round(cost, 4),
        "avg_latency_ms": round(latency / n, 1) if n else 0,
        "avg_quality": round(quality / n, 3) if n else 0,
        "series": series,
    }
