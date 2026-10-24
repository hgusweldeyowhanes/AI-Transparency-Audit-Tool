from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..schemas import OversightOut, ReviewIn, ReviewOut
from ..services.oversight import add_review, build_oversight, reviews_for

router = APIRouter(prefix="/v1/oversight", tags=["oversight"])


@router.get("", response_model=OversightOut)
def get_oversight(
    db: Session = Depends(get_db),
    status: str = Query("pending"),
    limit: int = Query(30, ge=1, le=100),
):
    if status not in ("pending", "reviewed", "all"):
        raise HTTPException(status_code=400, detail="status must be pending, reviewed, or all")
    return build_oversight(db, status=status, limit=limit)


@router.get("/events/{event_id}", response_model=List[ReviewOut])
def event_reviews(event_id: str, db: Session = Depends(get_db)):
    rows = reviews_for(db, event_id)
    if rows is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return rows


@router.post("", status_code=201, response_model=ReviewOut)
def create_review(payload: ReviewIn, db: Session = Depends(get_db), _: str = Depends(require_api_key)):
    row = add_review(db, payload)
    if row is None:
        raise HTTPException(status_code=404, detail="Event not found")
    db.commit()
    db.refresh(row)
    return row.to_dict()
