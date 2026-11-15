from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..services.chain import verify_chain
from ..services.retention import run_retention

router = APIRouter(prefix="/v1", tags=["integrity"], dependencies=[Depends(require_api_key)])


@router.get("/integrity/verify")
def integrity_verify(db: Session = Depends(get_db)):
    return verify_chain(db)


@router.post("/admin/retention/run")
def retention_run(retention_days: int = None, db: Session = Depends(get_db)):
    return run_retention(db, retention_days=retention_days)
