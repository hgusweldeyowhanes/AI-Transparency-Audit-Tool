import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import TrialLead
from ..schemas import TrialIn, TrialOut

router = APIRouter(prefix="/v1/trial", tags=["trial"])


@router.post("", response_model=TrialOut)
def start_trial(payload: TrialIn, db: Session = Depends(get_db)):
    lead = TrialLead(
        id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        email=payload.email,
        company=payload.company,
        use_case=payload.use_case,
        api_key=settings.api_key,
    )
    db.add(lead)
    db.commit()
    return TrialOut(
        api_key=settings.api_key,
        message="Trial recorded. Use this key for ingest. Demo data is already loaded in the dashboard.",
        dashboard_path="/app",
    )
