import re
from collections import defaultdict
from typing import Dict, List

from sqlalchemy.orm import Session

from ..models import AuditEvent
from .ingest import loads_list

TAXONOMY = {
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


def _normalize(text):
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text[:80]


def cluster_failures(db: Session, limit=40):
    rows = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(2000).all()
    by_flag = defaultdict(int)  # type: Dict[str, int]
    clusters = defaultdict(lambda: {"count": 0, "flag": "", "sample": "", "event_ids": []})
    failed_events = 0
    for r in rows:
        flags = loads_list(r.failure_flags)
        if not flags:
            continue
        failed_events += 1
        for f in flags:
            by_flag[f] += 1
            key = f + "::" + _normalize(r.completion)
            c = clusters[key]
            c["count"] += 1
            c["flag"] = f
            if not c["sample"]:
                c["sample"] = (r.completion or "")[:280]
            if len(c["event_ids"]) < 5:
                c["event_ids"].append(r.id)

    ranked = sorted(clusters.values(), key=lambda x: x["count"], reverse=True)[:limit]
    taxonomy = [
        {
            "flag": flag,
            "label": TAXONOMY.get(flag, flag),
            "count": count,
        }
        for flag, count in sorted(by_flag.items(), key=lambda kv: kv[1], reverse=True)
    ]
    return {
        "scanned": len(rows),
        "failed_events": failed_events,
        "taxonomy": taxonomy,
        "clusters": ranked,
    }
