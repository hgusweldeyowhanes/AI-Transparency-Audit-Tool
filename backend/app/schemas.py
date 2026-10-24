from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(from_attributes=True)


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


DECISIONS = ("confirmed", "false_positive", "escalated", "cleared")


class ReviewIn(BaseModel):
    event_id: str = Field(min_length=1, max_length=36)
    reviewer: str = Field(min_length=1, max_length=80)
    decision: str
    note: str = Field(default="", max_length=2000)

    @field_validator("reviewer", "note")
    @classmethod
    def strip_text(cls, value):
        return value.strip()

    @field_validator("reviewer")
    @classmethod
    def reviewer_present(cls, value):
        if not value:
            raise ValueError("reviewer is required")
        return value

    @field_validator("decision")
    @classmethod
    def known_decision(cls, value):
        if value not in DECISIONS:
            raise ValueError("decision must be confirmed, false_positive, escalated, or cleared")
        return value


class ReviewOut(BaseModel):
    id: str
    event_id: str
    created_at: datetime
    reviewer: str
    decision: str
    note: str


class OversightStats(BaseModel):
    flagged_events: int
    reviewed: int
    pending: int
    coverage: float
    confirmed: int
    false_positive: int
    escalated: int
    cleared: int


class QueueItem(BaseModel):
    id: str
    timestamp: datetime
    model: str
    prompt_version: Optional[str] = None
    failure_flags: List[str]
    quality_score: float
    prompt: str
    completion: str
    review: Optional[ReviewOut] = None


class OversightOut(BaseModel):
    stats: OversightStats
    queue: List[QueueItem]
    recent: List[ReviewOut]
