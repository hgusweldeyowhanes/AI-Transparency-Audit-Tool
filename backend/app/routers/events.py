from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..repositories import EventStore
from ..schemas import EventBatchIn, EventIn, EventListOut, EventOut
from ..services.ingest import persist_event

router = APIRouter(prefix="/v1/events", tags=["events"])


@router.post("", status_code=201, response_model=EventOut)
def ingest_one(payload: EventIn, db: Session = Depends(get_db), _: str = Depends(require_api_key)):
    row = persist_event(db, payload)
    db.commit()
    db.refresh(row)
    return row.to_dict()


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
    total, rows = EventStore(db).search(
        q=q,
        model=model,
        flag=flag,
        tag=tag,
        prompt_version=prompt_version,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )
    return {"total": total, "events": [row.to_dict() for row in rows]}


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    row = EventStore(db).get(event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row.to_dict()
