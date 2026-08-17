from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..models import AuditEvent
from ..schemas import EventBatchIn, EventIn, EventListOut
from ..services.ingest import event_to_dict, loads_list, persist_event

router = APIRouter(prefix="/v1/events", tags=["events"])


@router.post("", status_code=201)
def ingest_one(payload: EventIn, db: Session = Depends(get_db), _: str = Depends(require_api_key)):
    row = persist_event(db, payload)
    db.commit()
    db.refresh(row)
    return event_to_dict(row)


@router.post("/batch", status_code=201)
def ingest_batch(payload: EventBatchIn, db: Session = Depends(get_db), _: str = Depends(require_api_key)):
    rows = [persist_event(db, item) for item in payload.events]
    db.commit()
    return {"ingested": len(rows), "ids": [r.id for r in rows]}


@router.get("", response_model=EventListOut)
def list_events(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    model: Optional[str] = None,
    flag: Optional[str] = None,
    tag: Optional[str] = None,
    prompt_version: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(AuditEvent)
    if model:
        query = query.filter(AuditEvent.model == model)
    if prompt_version:
        query = query.filter(AuditEvent.prompt_version == prompt_version)
    if since:
        query = query.filter(AuditEvent.timestamp >= since)
    if until:
        query = query.filter(AuditEvent.timestamp <= until)
    if q:
        like = "%" + q + "%"
        query = query.filter(
            (AuditEvent.prompt.like(like)) | (AuditEvent.completion.like(like)) | (AuditEvent.id.like(like))
        )
    rows = query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit * 4).all()
    filtered = []
    for r in rows:
        flags = loads_list(r.failure_flags)
        tags = loads_list(r.tags)
        if flag and flag not in flags:
            continue
        if tag and tag not in tags:
            continue
        filtered.append(r)
        if len(filtered) >= limit:
            break
    # Approximate total
    total = query.count()
    return {"total": total, "events": [event_to_dict(r) for r in filtered]}


@router.get("/{event_id}")
def get_event(event_id: str, db: Session = Depends(get_db)):
    row = db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
    if not row:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Event not found")
    return event_to_dict(row)
