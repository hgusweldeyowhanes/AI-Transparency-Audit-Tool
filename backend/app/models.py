from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base
from .jsoncols import JsonDict, JsonList


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    trace_id = Column(String(36), index=True, nullable=False)
    model = Column(String(128), index=True, nullable=False)
    provider = Column(String(64), nullable=False)
    prompt = Column(Text, nullable=False)
    completion = Column(Text, nullable=False, default="")
    system_prompt = Column(Text, nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)
    prompt_version = Column(String(64), index=True, nullable=True)
    user_id = Column(String(128), nullable=True)
    session_id = Column(String(128), index=True, nullable=True)
    tags = Column(JsonList, default=list)
    extra_metadata = Column("metadata", JsonDict, default=dict)
    failure_flags = Column(JsonList, default=list)
    quality_score = Column(Float, default=1.0)

    @property
    def flags(self):
        return self.failure_flags or []

    @property
    def failed(self):
        return bool(self.flags)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "trace_id": self.trace_id,
            "model": self.model,
            "provider": self.provider,
            "prompt": self.prompt,
            "completion": self.completion,
            "system_prompt": self.system_prompt,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "prompt_version": self.prompt_version,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tags": self.tags or [],
            "metadata": self.extra_metadata or {},
            "failure_flags": self.flags,
            "quality_score": self.quality_score,
        }


class TrialLead(Base):
    __tablename__ = "trial_leads"

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    email = Column(String(256), nullable=False)
    company = Column(String(256), nullable=True)
    use_case = Column(String(512), nullable=True)
    api_key = Column(String(128), nullable=False)
