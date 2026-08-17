import re
from collections import defaultdict

from ..repositories import EventStore
from .detectors import FLAG_LABELS


def _normalize(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())[:80]


def cluster_failures(db, limit=40):
    rows = EventStore(db).latest(2000)
    by_flag = defaultdict(int)
    clusters = defaultdict(lambda: {"count": 0, "flag": "", "sample": "", "event_ids": []})
    failed_events = 0
    for row in rows:
        if not row.failed:
            continue
        failed_events += 1
        for flag in row.flags:
            by_flag[flag] += 1
            cluster = clusters[flag + "::" + _normalize(row.completion)]
            cluster["count"] += 1
            cluster["flag"] = flag
            if not cluster["sample"]:
                cluster["sample"] = (row.completion or "")[:280]
            if len(cluster["event_ids"]) < 5:
                cluster["event_ids"].append(row.id)

    return {
        "scanned": len(rows),
        "failed_events": failed_events,
        "taxonomy": [
            {"flag": flag, "label": FLAG_LABELS.get(flag, flag), "count": count}
            for flag, count in sorted(by_flag.items(), key=lambda item: item[1], reverse=True)
        ],
        "clusters": sorted(clusters.values(), key=lambda item: item["count"], reverse=True)[:limit],
    }
