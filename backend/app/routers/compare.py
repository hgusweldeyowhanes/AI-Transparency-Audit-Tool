from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.compare import compare_models

router = APIRouter(prefix="/v1/compare", tags=["compare"])


@router.get("")
def compare(db: Session = Depends(get_db), days: int = Query(30, ge=1, le=365)):
    return compare_models(db, days=days)
