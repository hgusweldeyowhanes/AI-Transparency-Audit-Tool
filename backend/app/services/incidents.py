"""Incident workflow linked to drift / flagged traffic."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..clock import utc_now
from ..models import Incident

SEVERITIES = ("low", "medium", "high", "critical")
STATUSES = ("open", "investigating", "resolved", "dismissed")


def list_incidents(db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
    q = db.query(Incident).order_by(Incident.updated_at.desc())
    if status:
        q = q.filter(Incident.status == status)
    return [i.to_dict() for i in q.all()]


def create_incident(db: Session, data: Dict[str, Any]) -> Incident:
    severity = data.get("severity") or "medium"
    status = data.get("status") or "open"
    if severity not in SEVERITIES:
        raise ValueError("invalid severity")
    if status not in STATUSES:
        raise ValueError("invalid status")
    row = Incident(
        id=str(uuid.uuid4()),
        title=data["title"].strip(),
        severity=severity,
        status=status,
        owner=data.get("owner") or "unassigned",
        metric=data.get("metric"),
        detail=data.get("detail") or "",
        rca=data.get("rca") or "",
        linked_event_ids=data.get("linked_event_ids") or [],
        prompt_version=data.get("prompt_version"),
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_incident(db: Session, incident_id: str, data: Dict[str, Any]) -> Incident:
    row = db.query(Incident).filter(Incident.id == incident_id).first()
    if not row:
        raise KeyError(incident_id)
    if "title" in data and data["title"]:
        row.title = data["title"].strip()
    if "severity" in data and data["severity"]:
        if data["severity"] not in SEVERITIES:
            raise ValueError("invalid severity")
        row.severity = data["severity"]
    if "status" in data and data["status"]:
        if data["status"] not in STATUSES:
            raise ValueError("invalid status")
        row.status = data["status"]
        if data["status"] == "resolved" and not row.resolved_at:
            row.resolved_at = utc_now()
    if "owner" in data and data["owner"] is not None:
        row.owner = data["owner"]
    if "detail" in data and data["detail"] is not None:
        row.detail = data["detail"]
    if "rca" in data and data["rca"] is not None:
        row.rca = data["rca"]
    if "linked_event_ids" in data and data["linked_event_ids"] is not None:
        row.linked_event_ids = data["linked_event_ids"]
    if "prompt_version" in data:
        row.prompt_version = data["prompt_version"]
    if "metric" in data:
        row.metric = data["metric"]
    row.updated_at = utc_now()
    db.commit()
    db.refresh(row)
    return row


def seed_demo_incident(db: Session) -> None:
    if db.query(Incident).count():
        return
    create_incident(
        db,
        {
            "title": "Prompt v2 factual-error spike",
            "severity": "high",
            "status": "resolved",
            "owner": "support-eng",
            "metric": "factual_error_rate",
            "prompt_version": "v2",
            "detail": (
                "Demo case study: aggressive prompt v2 lifted ungrounded policy citations "
                "for ~5 days before rollback to v1."
            ),
            "rca": (
                "Root cause: prompt instructed the model to invent helpful policy references. "
                "Fix: deprecate v2, require groundedness >= 0.45 under rubric-v1, "
                "and require registry approval before production prompt changes."
            ),
            "linked_event_ids": [],
        },
    )
