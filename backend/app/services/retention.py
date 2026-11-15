"""Retention with chain-preserving soft purge (redact payloads, keep hashes)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from sqlalchemy.orm import Session

from ..clock import utc_now
from ..config import settings
from ..models import AuditEvent

REDACTED = "[redacted-under-retention]"


def run_retention(db: Session, retention_days: int = None) -> Dict[str, Any]:
    """
    Redact prompt/completion older than retention_days.

    Hash fields stay as written at ingest. Verification treats purged rows as
    intentionally redacted (link check only) so the chain remains auditable.
    """
    days = retention_days if retention_days is not None else settings.retention_days
    cutoff = utc_now() - timedelta(days=days)
    rows = (
        db.query(AuditEvent)
        .filter(AuditEvent.timestamp < cutoff)
        .filter(AuditEvent.purged_at.is_(None))
        .all()
    )
    for row in rows:
        row.prompt = REDACTED
        row.completion = REDACTED
        if row.system_prompt:
            row.system_prompt = REDACTED
        meta = dict(row.extra_metadata or {})
        meta["retention_purged"] = True
        meta["retention_cutoff"] = cutoff.isoformat()
        meta["original_event_hash"] = row.event_hash
        if "sources" in meta:
            meta["sources"] = ["[redacted]"]
        row.extra_metadata = meta
        row.purged_at = utc_now()
    db.commit()
    return {
        "retention_days": days,
        "cutoff": cutoff.isoformat() + "Z",
        "purged": len(rows),
        "note": (
            "Payloads redacted in place. event_hash still reflects the original "
            "ingest content; integrity verify marks these rows as redacted."
        ),
    }
