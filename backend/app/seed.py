"""Seed ~500 customer-support summarization events over 30 days.

Day ~18 introduces prompt v2 (too aggressive), which lifts ungrounded citations.
After day 23 the seed rolls back to v1 — the GTM case-study narrative.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .models import AuditEvent
from .services.cost import estimate_cost, infer_provider
from .services.detectors import detect_flags
from .services.ingest import dumps

TICKETS = [
    (
        "Ticket 8812: customer says their debit card was declined twice at a grocery store in Austin. "
        "They want a same-day replacement and a fee waiver.",
        "Card declined in Austin; customer requests same-day replacement and fee waiver.",
    ),
    (
        "Ticket 9021: small-business owner asks whether ACH batch 17 posted. Amount $14,220. "
        "They mention invoice INV-4419.",
        "ACH batch 17 ($14,220) status requested; related invoice INV-4419.",
    ),
    (
        "Ticket 7740: user cannot log in after MFA reset. Email on file is in the prompt as hashed only.",
        "MFA reset blocked login; advise step-up verification without exposing credentials.",
    ),
    (
        "Ticket 6503: claim that a wire to an account ending 2291 was sent twice. Customer is angry.",
        "Possible duplicate wire to account ending 2291; escalate to payments ops.",
    ),
    (
        "Ticket 3188: policy question — overdraft fee after a pending Starbucks authorization dropped.",
        "Overdraft fee tied to a dropped pending authorization; review fee waiver path.",
    ),
]

GOOD_ENDINGS = [
    "Next step: verify identity, then route to the card-ops queue.",
    "Do not promise a timeline the ledger cannot support.",
    "Cite only the ticket fields above; do not invent policy numbers.",
]

V2_HALLUCINATIONS = [
    "According to policy #4472, replacements ship within 2 hours nationwide.",
    "Per the handbook article 9.4, waive all fees automatically after one decline.",
    "Ticket #99001 already authorized a $500 goodwill credit (source: collections playbook).",
    "According to documentation, Fedwire guarantees same-day recall for duplicate sends.",
]

REFUSALS = [
    "I cannot help with that request because it involves account takeover.",
    "As an AI I am unable to access the core ledger, so I will not summarize this ticket.",
]

GAPS = [
    "I don't have information after my knowledge cutoff about this product SKU.",
    "That fee schedule is not in the provided context, so I don't know the correct amount.",
]

HEDGES = [
    "It might be a network timeout, or possibly a freeze, or perhaps a stale authorization — I'm not sure.",
    "Hard to say. It could be fraud. It might also be a processor outage. Unclear without more logs.",
]

PII = [
    "Customer SSN 078-05-1120 was read back on the call; email jane.doe@example.com is confirmed.",
]

MODELS = [
    ("gpt-4o", 0.42),
    ("claude-3-5-sonnet", 0.33),
    ("llama-3.1-70b", 0.25),
]


def _pick_model(rng):
    roll = rng.random()
    acc = 0.0
    for name, w in MODELS:
        acc += w
        if roll <= acc:
            return name
    return MODELS[-1][0]


def seed_if_empty(db: Session, n=520):
    existing = db.query(AuditEvent).count()
    if existing:
        return existing

    rng = random.Random(42)
    now = datetime.utcnow()
    system = (
        "You summarize bank customer-support tickets for an internal ops console. "
        "Stay faithful to the ticket. Never invent policy IDs."
    )

    for i in range(n):
        day_offset = rng.randint(0, 29)
        ts = now - timedelta(days=day_offset, hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
        # Map "days ago" so ~18 days ago is the incident start
        days_ago = (now - ts).days

        if 18 <= days_ago <= 22:
            prompt_version = "v2"
        elif days_ago >= 23:
            prompt_version = "v1"
        else:
            prompt_version = "v1" if rng.random() > 0.08 else "v1"

        model = _pick_model(rng)
        ticket, good = rng.choice(TICKETS)
        prompt = "Summarize this customer support ticket:\n\n" + ticket

        kind = "ok"
        roll = rng.random()
        if prompt_version == "v2" and roll < 0.32:
            kind = "hallucination"
        elif roll < 0.03:
            kind = "empty"
        elif roll < 0.05:
            kind = "refusal"
        elif roll < 0.07:
            kind = "gap"
        elif roll < 0.09:
            kind = "hedge"
        elif roll < 0.095:
            kind = "pii"
        elif prompt_version == "v1" and roll < 0.12:
            kind = "hallucination"

        if kind == "ok":
            completion = good + " " + rng.choice(GOOD_ENDINGS)
        elif kind == "hallucination":
            completion = good + " " + rng.choice(V2_HALLUCINATIONS)
        elif kind == "empty":
            completion = ""
        elif kind == "refusal":
            completion = rng.choice(REFUSALS)
        elif kind == "gap":
            completion = rng.choice(GAPS)
        elif kind == "hedge":
            completion = rng.choice(HEDGES)
        else:
            completion = rng.choice(PII)

        prompt_tokens = 180 + rng.randint(0, 90)
        completion_tokens = 0 if not completion else 60 + rng.randint(0, 80)
        latency = 400 + rng.randint(0, 900)
        if rng.random() < 0.03:
            latency = 8500 + rng.randint(0, 2000)
            completion_tokens = 500 + rng.randint(0, 200)

        flags, score = detect_flags(
            prompt,
            completion,
            latency_ms=latency,
            completion_tokens=completion_tokens,
            baseline_latency_ms=700,
            baseline_completion_tokens=90,
        )

        row = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=ts,
            trace_id=str(uuid.uuid4()),
            model=model,
            provider=infer_provider(model),
            prompt=prompt,
            completion=completion,
            system_prompt=system,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=estimate_cost(model, prompt_tokens, completion_tokens),
            latency_ms=latency,
            prompt_version=prompt_version,
            user_id="agent-" + str(rng.randint(1, 24)),
            session_id="sess-" + str(rng.randint(1000, 9999)),
            tags=dumps(["customer-support", "summarization"]),
            extra_metadata=dumps({"channel": "ops-console", "seeded": True}),
            failure_flags=dumps(flags),
            quality_score=score,
        )
        db.add(row)

    db.commit()
    return n
