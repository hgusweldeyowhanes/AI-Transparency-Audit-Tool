"""Prompt and model registry with approval states."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..clock import utc_now
from ..models import ModelRegistryEntry, PromptVersionEntry

MODEL_STATUSES = ("candidate", "approved", "deprecated")
PROMPT_STATUSES = ("draft", "approved", "deprecated")


def list_models(db: Session) -> List[Dict[str, Any]]:
    return [m.to_dict() for m in db.query(ModelRegistryEntry).order_by(ModelRegistryEntry.name.asc()).all()]


def upsert_model(db: Session, data: Dict[str, Any]) -> ModelRegistryEntry:
    name = data["name"]
    row = db.query(ModelRegistryEntry).filter(ModelRegistryEntry.name == name).first()
    if not row:
        row = ModelRegistryEntry(id=str(uuid.uuid4()), name=name, created_at=utc_now())
        db.add(row)
    row.provider = data.get("provider") or row.provider or "unknown"
    status = data.get("status") or row.status or "candidate"
    if status not in MODEL_STATUSES:
        raise ValueError("status must be candidate, approved, or deprecated")
    row.status = status
    row.owner = data.get("owner") or row.owner
    row.notes = data.get("notes") if data.get("notes") is not None else row.notes
    row.updated_at = utc_now()
    db.commit()
    db.refresh(row)
    return row


def list_prompts(db: Session) -> List[Dict[str, Any]]:
    return [
        p.to_dict()
        for p in db.query(PromptVersionEntry).order_by(PromptVersionEntry.updated_at.desc()).all()
    ]


def upsert_prompt(db: Session, data: Dict[str, Any]) -> PromptVersionEntry:
    version = data["version"]
    row = db.query(PromptVersionEntry).filter(PromptVersionEntry.version == version).first()
    content = data.get("content") or (row.content if row else "")
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if not row:
        row = PromptVersionEntry(
            id=str(uuid.uuid4()),
            version=version,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(row)
    row.model = data.get("model") or row.model
    status = data.get("status") or row.status or "draft"
    if status not in PROMPT_STATUSES:
        raise ValueError("status must be draft, approved, or deprecated")
    prev = row.status
    row.status = status
    row.owner = data.get("owner") or row.owner
    row.notes = data.get("notes") if data.get("notes") is not None else row.notes
    row.content = content
    row.content_hash = content_hash
    row.updated_at = utc_now()
    if status == "approved" and prev != "approved":
        row.approved_at = utc_now()
    db.commit()
    db.refresh(row)
    return row


def seed_registry(db: Session) -> None:
    if db.query(ModelRegistryEntry).count() == 0:
        for name, provider, status, owner in (
            ("gpt-4o", "openai", "approved", "platform"),
            ("claude-3-5-sonnet", "anthropic", "approved", "platform"),
            ("llama-3.1-70b", "meta", "candidate", "ml-eng"),
        ):
            upsert_model(
                db,
                {
                    "name": name,
                    "provider": provider,
                    "status": status,
                    "owner": owner,
                    "notes": "Seeded from demo traffic",
                },
            )
    if db.query(PromptVersionEntry).count() == 0:
        upsert_prompt(
            db,
            {
                "version": "v1",
                "model": "gpt-4o",
                "status": "approved",
                "owner": "support-eng",
                "content": (
                    "You summarize bank customer-support tickets for an internal ops console. "
                    "Stay faithful to the ticket. Never invent policy IDs."
                ),
                "notes": "Stable baseline",
            },
        )
        upsert_prompt(
            db,
            {
                "version": "v2",
                "model": "gpt-4o",
                "status": "deprecated",
                "owner": "support-eng",
                "content": (
                    "Summarize tickets aggressively and cite policies when helpful, "
                    "even if the ticket does not name them."
                ),
                "notes": "Rolled back after factual-error spike (demo incident)",
            },
        )
