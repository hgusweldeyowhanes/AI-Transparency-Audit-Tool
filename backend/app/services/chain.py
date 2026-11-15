"""Append-only hash chain for audit events (tamper-evident evidence)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models import AuditEvent, ChainMeta

GENESIS = "0" * 64


def _canon(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def event_digest(payload: Dict[str, Any], prev_hash: str) -> str:
    body = _canon({"prev": prev_hash, "event": payload})
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def payload_from_row(row: AuditEvent) -> Dict[str, Any]:
    return {
        "id": row.id,
        "timestamp": row.timestamp.isoformat() if row.timestamp else None,
        "trace_id": row.trace_id,
        "model": row.model,
        "provider": row.provider,
        "prompt": row.prompt,
        "completion": row.completion,
        "system_prompt": row.system_prompt,
        "prompt_tokens": row.prompt_tokens,
        "completion_tokens": row.completion_tokens,
        "cost_usd": round(float(row.cost_usd or 0.0), 8),
        "latency_ms": row.latency_ms,
        "prompt_version": row.prompt_version,
        "user_id": row.user_id,
        "session_id": row.session_id,
        "tags": row.tags or [],
        "metadata": row.extra_metadata or {},
        "failure_flags": row.failure_flags or [],
        "quality_score": row.quality_score,
        "judge_rubric_version": row.judge_rubric_version,
        "judge_scores": row.judge_scores or {},
        "groundedness_score": row.groundedness_score,
    }


def tip(db: Session) -> Tuple[str, int]:
    meta = db.get(ChainMeta, 1)
    if meta:
        return meta.tip_hash or GENESIS, int(meta.tip_index if meta.tip_index is not None else -1)
    last = (
        db.query(AuditEvent)
        .filter(AuditEvent.event_hash.isnot(None))
        .order_by(AuditEvent.chain_index.desc())
        .first()
    )
    if last and last.event_hash is not None:
        return last.event_hash, int(last.chain_index)
    return GENESIS, -1


def _set_tip(db: Session, tip_hash: str, tip_index: int) -> None:
    meta = db.get(ChainMeta, 1)
    if not meta:
        meta = ChainMeta(id=1, tip_hash=tip_hash, tip_index=tip_index)
        db.add(meta)
        db.flush()
    else:
        meta.tip_hash = tip_hash
        meta.tip_index = tip_index


def seal_event(db: Session, row: AuditEvent) -> AuditEvent:
    prev_hash, prev_index = tip(db)
    digest = event_digest(payload_from_row(row), prev_hash)
    row.prev_hash = prev_hash
    row.event_hash = digest
    row.chain_index = prev_index + 1
    _set_tip(db, digest, row.chain_index)
    return row


def verify_chain(db: Session, limit: Optional[int] = None) -> Dict[str, Any]:
    q = db.query(AuditEvent).order_by(AuditEvent.chain_index.asc(), AuditEvent.timestamp.asc())
    if limit:
        q = q.limit(limit)
    rows = q.all()
    expected_prev = GENESIS
    checked = 0
    broken_at = None
    gaps = 0
    redacted = 0
    for row in rows:
        if row.event_hash is None or row.chain_index is None:
            gaps += 1
            continue
        checked += 1
        if (row.prev_hash or GENESIS) != expected_prev:
            broken_at = {
                "event_id": row.id,
                "chain_index": row.chain_index,
                "reason": "prev_hash mismatch",
                "expected_prev": expected_prev,
                "actual_prev": row.prev_hash,
            }
            break
        if getattr(row, "purged_at", None):
            # Soft-purged: payload no longer matches original digest; chain link still checked.
            redacted += 1
        else:
            recomputed = event_digest(payload_from_row(row), row.prev_hash or GENESIS)
            if recomputed != row.event_hash:
                broken_at = {
                    "event_id": row.id,
                    "chain_index": row.chain_index,
                    "reason": "content hash mismatch (row may have been altered)",
                    "expected_hash": recomputed,
                    "stored_hash": row.event_hash,
                }
                break
        expected_prev = row.event_hash
    tip_hash, tip_index = tip(db)
    return {
        "ok": broken_at is None,
        "checked": checked,
        "unsealed": gaps,
        "redacted": redacted,
        "tip_hash": tip_hash,
        "tip_index": tip_index,
        "broken_at": broken_at,
        "genesis": GENESIS,
    }


def backfill_chain(db: Session) -> int:
    """Seal any events missing hashes, in timestamp order."""
    rows = (
        db.query(AuditEvent)
        .filter((AuditEvent.event_hash.is_(None)) | (AuditEvent.chain_index.is_(None)))
        .order_by(AuditEvent.timestamp.asc(), AuditEvent.id.asc())
        .all()
    )
    # If some are sealed and some are not, reseal everything chronologically for a clean chain.
    if rows and db.query(AuditEvent).filter(AuditEvent.event_hash.isnot(None)).count():
        all_rows = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc(), AuditEvent.id.asc()).all()
        _set_tip(db, GENESIS, -1)
        for row in all_rows:
            row.prev_hash = None
            row.event_hash = None
            row.chain_index = None
            seal_event(db, row)
        db.commit()
        return len(all_rows)
    for row in rows:
        seal_event(db, row)
    if rows:
        db.commit()
    return len(rows)
