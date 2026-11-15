from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_api_key
from ..services import registry as reg

router = APIRouter(prefix="/v1/registry", tags=["registry"], dependencies=[Depends(require_api_key)])


class ModelIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    provider: Optional[str] = "unknown"
    status: Optional[str] = "candidate"
    owner: Optional[str] = None
    notes: Optional[str] = None


class PromptIn(BaseModel):
    version: str = Field(min_length=1, max_length=64)
    model: Optional[str] = None
    status: Optional[str] = "draft"
    owner: Optional[str] = None
    notes: Optional[str] = None
    content: Optional[str] = ""


@router.get("/models")
def models(db: Session = Depends(get_db)):
    return {"models": reg.list_models(db)}


@router.post("/models")
def upsert_model(body: ModelIn, db: Session = Depends(get_db)):
    try:
        row = reg.upsert_model(db, body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return row.to_dict()


@router.get("/prompts")
def prompts(db: Session = Depends(get_db)):
    return {"prompts": reg.list_prompts(db)}


@router.post("/prompts")
def upsert_prompt(body: PromptIn, db: Session = Depends(get_db)):
    try:
        row = reg.upsert_prompt(db, body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return row.to_dict()
