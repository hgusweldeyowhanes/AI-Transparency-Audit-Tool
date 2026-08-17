"""Heuristic failure detectors — signals for operators, not ground-truth labels."""

from __future__ import annotations

import re
from typing import List, Optional, Sequence, Tuple

REFUSAL_RE = re.compile(
    r"\b(i (cannot|can't|won't|will not|am unable to|am not able to)|as an ai|i'm not able to)\b",
    re.I,
)
KNOWLEDGE_GAP_RE = re.compile(
    r"(knowledge cutoff|i don't have (enough )?information|i do not have (enough )?information|"
    r"i don't know|i do not know|not (present )?in (the )?(provided )?context|"
    r"outside (of )?my (training|knowledge))",
    re.I,
)
HEDGE_RE = re.compile(
    r"\b(might|possibly|perhaps|probably|i'm not sure|it could be|hard to say|unclear)\b",
    re.I,
)
CITATION_RE = re.compile(
    r"(according to|per (the )?(policy|doc|article)|policy\s*#?\d+|ticket\s*#?\d+|source:)",
    re.I,
)
POLICY_ID_RE = re.compile(r"(policy\s*#?\d+|ticket\s*#?\d+)", re.I)
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

FLAG_WEIGHTS = {
    "empty": 0.45,
    "truncated": 0.20,
    "refusal": 0.25,
    "knowledge_gap": 0.20,
    "hedging": 0.08,
    "factual_error": 0.30,
    "pii_leak": 0.35,
    "latency_anomaly": 0.10,
    "length_anomaly": 0.10,
}

FLAG_LABELS = {
    "empty": "Empty or near-empty completion",
    "truncated": "Output appears cut off",
    "refusal": "Model refused the task",
    "knowledge_gap": "Missing context or knowledge cutoff",
    "hedging": "High uncertainty language",
    "factual_error": "Ungrounded citation / likely hallucination",
    "pii_leak": "Possible PII in the completion",
    "latency_anomaly": "Unusually slow response",
    "length_anomaly": "Unusually long completion",
}


def _unique(flags):
    seen = set()
    ordered = []
    for flag in flags:
        if flag not in seen:
            seen.add(flag)
            ordered.append(flag)
    return ordered


def _ungrounded_citation(prompt, completion):
    prompt_l = prompt.lower()
    for ident in POLICY_ID_RE.findall(completion):
        if ident.lower() not in prompt_l:
            return True
    if CITATION_RE.search(completion) and not CITATION_RE.search(prompt):
        return bool(re.search(r"according to .{0,40}(policy|documentation|handbook|article)", completion, re.I))
    return False


def _quality_score(flags):
    score = 1.0
    for flag in flags:
        score -= FLAG_WEIGHTS.get(flag, 0.1)
    return max(0.05, min(1.0, round(score, 3)))


def detect_flags(
    prompt,
    completion,
    latency_ms=0,
    completion_tokens=0,
    baseline_latency_ms=None,
    baseline_completion_tokens=None,
):
    # type: (str, str, int, int, Optional[float], Optional[float]) -> Tuple[List[str], float]
    flags = []  # type: List[str]
    text = (completion or "").strip()
    prompt = prompt or ""

    if not text or (len(text) < 12 and completion_tokens < 8):
        flags.append("empty")
    if text.endswith(("...", "…")) or (completion_tokens > 0 and text.endswith((",", ";", "—"))):
        flags.append("truncated")
    if text and REFUSAL_RE.search(text):
        flags.append("refusal")
    if text and KNOWLEDGE_GAP_RE.search(text):
        flags.append("knowledge_gap")
    if text and len(HEDGE_RE.findall(text)) >= 3:
        flags.append("hedging")
    if text and _ungrounded_citation(prompt, text):
        flags.append("factual_error")
    if text and (EMAIL_RE.search(text) or SSN_RE.search(text) or CC_RE.search(text)):
        flags.append("pii_leak")
    if latency_ms >= 8000 or (
        baseline_latency_ms and latency_ms > baseline_latency_ms * 2.5 and latency_ms > 2500
    ):
        flags.append("latency_anomaly")
    if (
        baseline_completion_tokens
        and completion_tokens > baseline_completion_tokens * 3
        and completion_tokens > 400
    ):
        flags.append("length_anomaly")

    ordered = _unique(flags)
    return ordered, _quality_score(ordered)


def baseline_from_rows(latencies, completion_tokens):
    # type: (Sequence[int], Sequence[int]) -> Tuple[Optional[float], Optional[float]]
    def avg(values):
        values = [v for v in values if v]
        if not values:
            return None
        return sum(values) / float(len(values))

    return avg(latencies), avg(completion_tokens)
