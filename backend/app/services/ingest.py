import uuid

from sqlalchemy.orm import Session

from ..clock import utc_now
from ..models import AuditEvent
from ..repositories import EventStore
from ..schemas import EventIn
from .chain import seal_event
from .cost import estimate_cost, infer_provider
from .detectors import baseline_from_rows
from .judge import active_rubric, score_event


def persist_event(db, payload, run_detectors=True):
    # type: (Session, EventIn, bool) -> AuditEvent
    store = EventStore(db)
    lat_b = tok_b = None
    flags, score = [], 1.0
    judge_scores = {}
    groundedness = None
    rubric_version = None
    meta = dict(payload.metadata or {})
    sources = payload.sources or meta.get("sources") or meta.get("retrieved_docs")

    if run_detectors:
        lat_b, tok_b = baseline_from_rows(*store.recent_baselines())
        rubric = active_rubric(db)
        flags, score, judge_scores, groundedness = score_event(
            payload.prompt,
            payload.completion,
            rubric=rubric,
            sources=sources,
            latency_ms=payload.latency_ms or 0,
            completion_tokens=payload.completion_tokens or 0,
            baseline_latency_ms=lat_b,
            baseline_completion_tokens=tok_b,
        )
        rubric_version = rubric.version
        meta["judge"] = {
            "rubric_id": rubric.id,
            "rubric_version": rubric.version,
        }

    stamp = payload.timestamp.replace(tzinfo=None) if payload.timestamp else utc_now()
    row = AuditEvent(
        id=payload.id or str(uuid.uuid4()),
        timestamp=stamp,
        trace_id=payload.trace_id or str(uuid.uuid4()),
        model=payload.model,
        provider=infer_provider(payload.model, payload.provider),
        prompt=payload.prompt,
        completion=payload.completion or "",
        system_prompt=payload.system_prompt,
        prompt_tokens=payload.prompt_tokens or 0,
        completion_tokens=payload.completion_tokens or 0,
        cost_usd=payload.cost_usd
        if payload.cost_usd is not None
        else estimate_cost(payload.model, payload.prompt_tokens or 0, payload.completion_tokens or 0),
        latency_ms=payload.latency_ms or 0,
        prompt_version=payload.prompt_version,
        user_id=payload.user_id,
        session_id=payload.session_id,
        tags=payload.tags or [],
        extra_metadata=meta,
        failure_flags=flags,
        quality_score=score,
        judge_rubric_version=rubric_version,
        judge_scores=judge_scores,
        groundedness_score=groundedness,
    )
    db.add(row)
    db.flush()
    seal_event(db, row)
    return row
