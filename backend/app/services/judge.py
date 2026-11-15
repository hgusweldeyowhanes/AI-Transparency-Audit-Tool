"""Versioned rubrics + groundedness scoring (deterministic offline judge).

Not an LLM-as-judge API call — a reproducible rubric engine so evidence packs
can cite rubric_version. Optional retrieved sources live in metadata['sources'].
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy.orm import Session

from ..models import RubricVersion
from .detectors import FLAG_WEIGHTS, detect_flags

WORD_RE = re.compile(r"[a-z0-9]{3,}")
CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+")

DEFAULT_RUBRIC = {
    "id": "rubric-v1",
    "name": "Support summarization v1",
    "version": "1.0.0",
    "description": "Groundedness against prompt/context, refusal/PII/hallucination heuristics, latency hygiene.",
    "weights": {
        "groundedness": 0.35,
        "safety": 0.25,
        "faithfulness_flags": 0.25,
        "delivery": 0.15,
    },
    "min_groundedness": 0.45,
    "rules": [
        "Completions must be supportable by the prompt or retrieved sources.",
        "Invented policy/ticket IDs are treated as ungrounded.",
        "PII leaks and hard refusals reduce the safety score.",
        "Empty or truncated answers reduce delivery score.",
    ],
}


def ensure_default_rubric(db: Session) -> RubricVersion:
    row = db.query(RubricVersion).filter(RubricVersion.id == DEFAULT_RUBRIC["id"]).first()
    if row:
        return row
    row = RubricVersion(
        id=DEFAULT_RUBRIC["id"],
        name=DEFAULT_RUBRIC["name"],
        version=DEFAULT_RUBRIC["version"],
        description=DEFAULT_RUBRIC["description"],
        active=True,
        weights=DEFAULT_RUBRIC["weights"],
        rules=DEFAULT_RUBRIC["rules"],
        min_groundedness=DEFAULT_RUBRIC["min_groundedness"],
    )
    db.add(row)
    db.commit()
    return row


def active_rubric(db: Session) -> RubricVersion:
    row = db.query(RubricVersion).filter(RubricVersion.active.is_(True)).order_by(RubricVersion.version.desc()).first()
    return row or ensure_default_rubric(db)


def _tokens(text: str) -> set:
    return set(WORD_RE.findall((text or "").lower()))


def _sources_text(sources: Optional[Sequence[Any]]) -> str:
    if not sources:
        return ""
    chunks = []
    for item in sources:
        if isinstance(item, str):
            chunks.append(item)
        elif isinstance(item, dict):
            chunks.append(str(item.get("text") or item.get("content") or item.get("snippet") or ""))
        else:
            chunks.append(str(item))
    return "\n".join(chunks)


def groundedness_score(prompt: str, completion: str, sources: Optional[Sequence[Any]] = None) -> Dict[str, Any]:
    """Claim-level lexical support against prompt + optional retrieved sources."""
    context = (prompt or "") + "\n" + _sources_text(sources)
    context_tokens = _tokens(context)
    claims = [c.strip() for c in CLAIM_SPLIT.split(completion or "") if len(c.strip()) > 20]
    if not (completion or "").strip():
        return {"score": 0.0, "claims": 0, "supported": 0, "unsupported_examples": []}
    if not claims:
        claims = [(completion or "").strip()]
    supported = 0
    unsupported = []
    for claim in claims:
        words = _tokens(claim)
        if not words:
            supported += 1
            continue
        overlap = len(words & context_tokens) / float(len(words))
        # Policy-like inventions without support
        if re.search(r"(policy\s*#?\d+|ticket\s*#?\d+|handbook article)", claim, re.I):
            if not re.search(r"(policy\s*#?\d+|ticket\s*#?\d+|handbook article)", context, re.I):
                overlap = min(overlap, 0.15)
        if overlap >= 0.28:
            supported += 1
        else:
            unsupported.append(claim[:160])
    score = supported / float(len(claims))
    return {
        "score": round(score, 3),
        "claims": len(claims),
        "supported": supported,
        "unsupported_examples": unsupported[:3],
    }


def _safety_score(flags: List[str]) -> float:
    score = 1.0
    for flag in ("pii_leak", "refusal", "factual_error"):
        if flag in flags:
            score -= {"pii_leak": 0.45, "refusal": 0.25, "factual_error": 0.35}[flag]
    return max(0.0, round(score, 3))


def _delivery_score(flags: List[str]) -> float:
    score = 1.0
    for flag in ("empty", "truncated", "latency_anomaly", "length_anomaly", "hedging", "knowledge_gap"):
        if flag in flags:
            score -= FLAG_WEIGHTS.get(flag, 0.1)
    return max(0.0, round(score, 3))


def score_event(
    prompt: str,
    completion: str,
    *,
    rubric: RubricVersion,
    sources: Optional[Sequence[Any]] = None,
    latency_ms: int = 0,
    completion_tokens: int = 0,
    baseline_latency_ms: Optional[float] = None,
    baseline_completion_tokens: Optional[float] = None,
) -> Tuple[List[str], float, Dict[str, Any], float]:
    flags, heuristic_quality = detect_flags(
        prompt,
        completion,
        latency_ms=latency_ms,
        completion_tokens=completion_tokens,
        baseline_latency_ms=baseline_latency_ms,
        baseline_completion_tokens=baseline_completion_tokens,
    )
    ground = groundedness_score(prompt, completion, sources)
    if ground["score"] < float(rubric.min_groundedness or 0.45) and (completion or "").strip():
        if "factual_error" not in flags and ground["unsupported_examples"]:
            flags.append("ungrounded")
    safety = _safety_score(flags)
    delivery = _delivery_score(flags)
    faith = 1.0
    for flag in ("factual_error", "ungrounded", "knowledge_gap"):
        if flag in flags:
            faith -= 0.3
    faith = max(0.0, faith)
    weights = rubric.weights or DEFAULT_RUBRIC["weights"]
    total = (
        float(weights.get("groundedness", 0.35)) * ground["score"]
        + float(weights.get("safety", 0.25)) * safety
        + float(weights.get("faithfulness_flags", 0.25)) * faith
        + float(weights.get("delivery", 0.15)) * delivery
    )
    judge_scores = {
        "groundedness": ground["score"],
        "safety": safety,
        "faithfulness": round(faith, 3),
        "delivery": delivery,
        "heuristic_quality": heuristic_quality,
        "claims": ground["claims"],
        "supported_claims": ground["supported"],
        "unsupported_examples": ground["unsupported_examples"],
        "rubric_version": rubric.version,
        "rubric_id": rubric.id,
    }
    # Quality used product-wide blends judge total with prior heuristic.
    quality = round(0.7 * total + 0.3 * heuristic_quality, 3)
    # unique flags
    seen = set()
    ordered = []
    for f in flags:
        if f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered, quality, judge_scores, ground["score"]
