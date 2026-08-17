from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.drift import compute_drift

router = APIRouter(prefix="/v1/drift", tags=["drift"])


@router.get("")
def drift(db: Session = Depends(get_db)):
    return compute_drift(db)
