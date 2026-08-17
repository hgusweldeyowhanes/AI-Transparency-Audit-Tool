from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base


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
    tags = Column(Text, default="[]")  # JSON list
    extra_metadata = Column("metadata", Text, default="{}")  # JSON object
    failure_flags = Column(Text, default="[]")  # JSON list
    quality_score = Column(Float, default=1.0)


class TrialLead(Base):
    __tablename__ = "trial_leads"

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    email = Column(String(256), nullable=False)
    company = Column(String(256), nullable=True)
    use_case = Column(String(512), nullable=True)
    api_key = Column(String(128), nullable=False)
