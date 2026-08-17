from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.compliance import eu_ai_act_payload, render_html, sec_payload

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get("/eu-ai-act")
def eu_ai_act(db: Session = Depends(get_db), format: str = "json"):
    payload = eu_ai_act_payload(db)
    if format == "html":
        return HTMLResponse(render_html(payload["title"], payload["disclaimer"], payload))
    return payload


@router.get("/sec")
def sec(db: Session = Depends(get_db), format: str = "json"):
    payload = sec_payload(db)
    if format == "html":
        return HTMLResponse(render_html(payload["title"], payload["disclaimer"], payload))
    return payload
