from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..services import incidents as inc

router = APIRouter(prefix="/v1", tags=["incidents"], dependencies=[Depends(require_api_key)])


class IncidentIn(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    severity: Optional[str] = "medium"
    status: Optional[str] = "open"
    owner: Optional[str] = "unassigned"
    metric: Optional[str] = None
    detail: Optional[str] = ""
    rca: Optional[str] = ""
    linked_event_ids: Optional[List[str]] = None
    prompt_version: Optional[str] = None


class IncidentPatch(BaseModel):
    title: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    metric: Optional[str] = None
    detail: Optional[str] = None
    rca: Optional[str] = None
    linked_event_ids: Optional[List[str]] = None
    prompt_version: Optional[str] = None


@router.get("/incidents")
def list_incidents(status: Optional[str] = None, db: Session = Depends(get_db)):
    return {"incidents": inc.list_incidents(db, status=status)}


@router.post("/incidents")
def create_incident(body: IncidentIn, db: Session = Depends(get_db)):
    try:
        row = inc.create_incident(db, body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return row.to_dict()


@router.patch("/incidents/{incident_id}")
def patch_incident(incident_id: str, body: IncidentPatch, db: Session = Depends(get_db)):
    try:
        row = inc.update_incident(db, incident_id, body.model_dump(exclude_unset=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="incident not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return row.to_dict()
