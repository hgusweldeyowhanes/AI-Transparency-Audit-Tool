"""Heuristic failure detectors — no paid LLM required.

These flags are signals for operators, not ground-truth labels. They exist so
self-hosted installs can surface likely issues (empty replies, refusals,
citation-without-source) before investing in LLM-as-judge scoring.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Sequence, Tuple

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


def _count_hits(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text or ""))


def detect_flags(
    prompt: str,
    completion: str,
    latency_ms: int = 0,
    completion_tokens: int = 0,
    baseline_latency_ms: Optional[float] = None,
    baseline_completion_tokens: Optional[float] = None,
) -> Tuple[List[str], float]:
    flags = []  # type: List[str]
    text = (completion or "").strip()
    prompt_l = prompt or ""

    if not text:
        flags.append("empty")
    elif len(text) < 12 and completion_tokens < 8:
        flags.append("empty")

    if text.endswith(("...", "…")) or (completion_tokens > 0 and text.endswith((",", ";", "—"))):
        flags.append("truncated")

    if text and REFUSAL_RE.search(text):
        flags.append("refusal")

    if text and KNOWLEDGE_GAP_RE.search(text):
        flags.append("knowledge_gap")

    if text and _count_hits(HEDGE_RE, text) >= 3:
        flags.append("hedging")

    if text and CITATION_RE.search(text):
        cites = CITATION_RE.findall(text)
        grounded = 0
        for _ in cites:
            # If the completion cites a policy/ticket/source that never appeared
            # in the prompt, treat it as a hallucination proxy.
            snippet_match = re.search(r"(policy\s*#?\d+|ticket\s*#?\d+)", text, re.I)
            if snippet_match and snippet_match.group(0).lower() not in prompt_l.lower():
                flags.append("factual_error")
                break
            grounded += 1
        else:
            if CITATION_RE.search(text) and not CITATION_RE.search(prompt_l):
                # Generic "according to" with no grounding in the prompt.
                if re.search(r"according to .{0,40}(policy|documentation|handbook|article)", text, re.I):
                    flags.append("factual_error")

    if text and (EMAIL_RE.search(text) or SSN_RE.search(text) or CC_RE.search(text)):
        flags.append("pii_leak")

    if baseline_latency_ms and latency_ms > 0 and latency_ms > baseline_latency_ms * 2.5 and latency_ms > 2500:
        flags.append("latency_anomaly")
    elif latency_ms >= 8000:
        flags.append("latency_anomaly")

    if (
        baseline_completion_tokens
        and completion_tokens > 0
        and completion_tokens > baseline_completion_tokens * 3
        and completion_tokens > 400
    ):
        flags.append("length_anomaly")

    # Dedupe, keep stable order
    seen = set()
    ordered = []
    for f in flags:
        if f not in seen:
            seen.add(f)
            ordered.append(f)

    score = 1.0
    for f in ordered:
        score -= FLAG_WEIGHTS.get(f, 0.1)
    score = max(0.05, min(1.0, round(score, 3)))
    return ordered, score


def baseline_from_rows(latencies: Sequence[int], completion_tokens: Sequence[int]) -> Tuple[Optional[float], Optional[float]]:
    def avg(xs):
        xs = [x for x in xs if x]
        if not xs:
            return None
        return sum(xs) / float(len(xs))

    return avg(latencies), avg(completion_tokens)
