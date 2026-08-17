from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.drift import compute_metrics

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])


@router.get("")
def metrics(db: Session = Depends(get_db), days: int = Query(30, ge=1, le=365)):
    return compute_metrics(db, days=days)
