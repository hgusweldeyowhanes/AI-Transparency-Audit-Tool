import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models import AuditEvent
from .cost import estimate_cost, infer_provider
from .detectors import baseline_from_rows, detect_flags


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def dumps(value):
    return json.dumps(value or ([] if isinstance(value, list) else {}))


def loads_list(raw):
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except ValueError:
        return []


def loads_obj(raw):
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def event_to_dict(row):
    return {
        "id": row.id,
        "timestamp": row.timestamp,
        "trace_id": row.trace_id,
        "model": row.model,
        "provider": row.provider,
        "prompt": row.prompt,
        "completion": row.completion,
        "system_prompt": row.system_prompt,
        "prompt_tokens": row.prompt_tokens,
        "completion_tokens": row.completion_tokens,
        "cost_usd": row.cost_usd,
        "latency_ms": row.latency_ms,
        "prompt_version": row.prompt_version,
        "user_id": row.user_id,
        "session_id": row.session_id,
        "tags": loads_list(row.tags),
        "metadata": loads_obj(row.extra_metadata),
        "failure_flags": loads_list(row.failure_flags),
        "quality_score": row.quality_score,
    }


def recent_baselines(db: Session) -> Tuple[Optional[float], Optional[float]]:
    rows = (
        db.query(AuditEvent.latency_ms, AuditEvent.completion_tokens)
        .order_by(AuditEvent.timestamp.desc())
        .limit(80)
        .all()
    )
    return baseline_from_rows([r[0] for r in rows], [r[1] for r in rows])


def persist_event(db: Session, payload, run_detectors=True):
    lat_b, tok_b = recent_baselines(db) if run_detectors else (None, None)
    flags, score = ([], 1.0)
    if run_detectors:
        flags, score = detect_flags(
            payload.prompt,
            payload.completion,
            latency_ms=payload.latency_ms or 0,
            completion_tokens=payload.completion_tokens or 0,
            baseline_latency_ms=lat_b,
            baseline_completion_tokens=tok_b,
        )

    cost = payload.cost_usd
    if cost is None:
        cost = estimate_cost(payload.model, payload.prompt_tokens or 0, payload.completion_tokens or 0)

    row = AuditEvent(
        id=payload.id or str(uuid.uuid4()),
        timestamp=payload.timestamp.replace(tzinfo=None) if payload.timestamp else _now(),
        trace_id=payload.trace_id or str(uuid.uuid4()),
        model=payload.model,
        provider=infer_provider(payload.model, payload.provider),
        prompt=payload.prompt,
        completion=payload.completion or "",
        system_prompt=payload.system_prompt,
        prompt_tokens=payload.prompt_tokens or 0,
        completion_tokens=payload.completion_tokens or 0,
        cost_usd=cost,
        latency_ms=payload.latency_ms or 0,
        prompt_version=payload.prompt_version,
        user_id=payload.user_id,
        session_id=payload.session_id,
        tags=dumps(payload.tags),
        extra_metadata=dumps(payload.metadata),
        failure_flags=dumps(flags),
        quality_score=score,
    )
    db.add(row)
    return row
