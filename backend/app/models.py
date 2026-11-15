from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

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

    # Advanced evidence fields
    judge_rubric_version = Column(String(64), nullable=True)
    judge_scores = Column(JsonDict, default=dict)
    groundedness_score = Column(Float, nullable=True)
    prev_hash = Column(String(64), nullable=True)
    event_hash = Column(String(64), index=True, nullable=True)
    chain_index = Column(Integer, index=True, nullable=True)
    purged_at = Column(DateTime, nullable=True)

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
            "judge_rubric_version": self.judge_rubric_version,
            "judge_scores": self.judge_scores or {},
            "groundedness_score": self.groundedness_score,
            "prev_hash": self.prev_hash,
            "event_hash": self.event_hash,
            "chain_index": self.chain_index,
            "purged_at": self.purged_at,
        }


class OversightReview(Base):
    __tablename__ = "oversight_reviews"

    id = Column(String(36), primary_key=True)
    event_id = Column(String(36), index=True, nullable=False)
    created_at = Column(DateTime, index=True, nullable=False)
    reviewer = Column(String(80), nullable=False)
    decision = Column(String(32), nullable=False)
    note = Column(Text, nullable=False, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "created_at": self.created_at,
            "reviewer": self.reviewer,
            "decision": self.decision,
            "note": self.note or "",
        }


class TrialLead(Base):
    __tablename__ = "trial_leads"

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    email = Column(String(256), nullable=False)
    company = Column(String(256), nullable=True)
    use_case = Column(String(512), nullable=True)
    api_key = Column(String(128), nullable=False)


class ChainMeta(Base):
    __tablename__ = "chain_meta"

    id = Column(Integer, primary_key=True)
    tip_hash = Column(String(64), nullable=False, default="")
    tip_index = Column(Integer, nullable=False, default=-1)


class RubricVersion(Base):
    __tablename__ = "rubric_versions"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    weights = Column(JsonDict, default=dict)
    rules = Column(JsonList, default=list)
    min_groundedness = Column(Float, default=0.45)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "active": bool(self.active),
            "weights": self.weights or {},
            "rules": self.rules or [],
            "min_groundedness": self.min_groundedness,
        }


class ModelRegistryEntry(Base):
    __tablename__ = "model_registry"

    id = Column(String(36), primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    provider = Column(String(64), nullable=False, default="unknown")
    status = Column(String(32), nullable=False, default="candidate")
    owner = Column(String(80), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "status": self.status,
            "owner": self.owner,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PromptVersionEntry(Base):
    __tablename__ = "prompt_registry"

    id = Column(String(36), primary_key=True)
    version = Column(String(64), unique=True, nullable=False)
    model = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="draft")
    owner = Column(String(80), nullable=True)
    notes = Column(Text, nullable=True)
    content = Column(Text, nullable=False, default="")
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    approved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "model": self.model,
            "status": self.status,
            "owner": self.owner,
            "notes": self.notes,
            "content": self.content,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "approved_at": self.approved_at,
        }


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False, default="medium")
    status = Column(String(32), nullable=False, default="open")
    owner = Column(String(80), nullable=False, default="unassigned")
    metric = Column(String(64), nullable=True)
    detail = Column(Text, nullable=False, default="")
    rca = Column(Text, nullable=False, default="")
    linked_event_ids = Column(JsonList, default=list)
    prompt_version = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "status": self.status,
            "owner": self.owner,
            "metric": self.metric,
            "detail": self.detail,
            "rca": self.rca,
            "linked_event_ids": self.linked_event_ids or [],
            "prompt_version": self.prompt_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
        }
