from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..models import RubricVersion
from ..services.judge import ensure_default_rubric

router = APIRouter(prefix="/v1", tags=["rubrics"], dependencies=[Depends(require_api_key)])


@router.get("/rubrics")
def list_rubrics(db: Session = Depends(get_db)):
    ensure_default_rubric(db)
    rows = db.query(RubricVersion).order_by(RubricVersion.version.desc()).all()
    return {"rubrics": [r.to_dict() for r in rows]}
