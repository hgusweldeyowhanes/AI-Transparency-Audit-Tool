from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.clustering import cluster_failures

router = APIRouter(prefix="/v1/failures", tags=["failures"])


@router.get("")
def failures(db: Session = Depends(get_db), limit: int = Query(40, ge=1, le=100)):
    return cluster_failures(db, limit=limit)
