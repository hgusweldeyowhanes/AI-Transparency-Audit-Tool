from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    trace_id: Optional[str] = None
    model: str
    provider: Optional[str] = None
    prompt: str
    completion: str = ""
    system_prompt: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: Optional[float] = None
    latency_ms: int = 0
    prompt_version: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventBatchIn(BaseModel):
    events: List[EventIn]


class EventOut(BaseModel):
    id: str
    timestamp: datetime
    trace_id: str
    model: str
    provider: str
    prompt: str
    completion: str
    system_prompt: Optional[str] = None
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int
    prompt_version: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str]
    metadata: Dict[str, Any]
    failure_flags: List[str]
    quality_score: float

    class Config:
        from_attributes = True


class EventListOut(BaseModel):
    total: int
    events: List[EventOut]


class TrialIn(BaseModel):
    email: str
    company: Optional[str] = None
    use_case: Optional[str] = None


class TrialOut(BaseModel):
    api_key: str
    message: str
    dashboard_path: str = "/app"
