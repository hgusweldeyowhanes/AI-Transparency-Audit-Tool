"""Shared rollups used by metrics, drift, compare, and compliance packs."""

from collections import defaultdict
from datetime import timedelta
from typing import Any, Dict, Iterable

from ..clock import iso_z, utc_now
from ..models import AuditEvent


def summarize(rows):
    # type: (Iterable[AuditEvent]) -> Dict[str, Any]
    rows = list(rows)
    n = len(rows)
    empty = {
        "events": 0,
        "failed": 0,
        "failure_rate": 0.0,
        "avg_latency_ms": 0.0,
        "avg_cost_usd": 0.0,
        "avg_output_tokens": 0.0,
        "avg_quality": 0.0,
        "total_cost_usd": 0.0,
    }
    if n == 0:
        return empty
    failed = 0
    lat = cost = toks = qual = 0.0
    for row in rows:
        if row.failed:
            failed += 1
        lat += row.latency_ms or 0
        cost += row.cost_usd or 0
        toks += row.completion_tokens or 0
        qual += row.quality_score or 0
    return {
        "events": n,
        "failed": failed,
        "failure_rate": round(failed / float(n), 4),
        "avg_latency_ms": round(lat / n, 1),
        "avg_cost_usd": round(cost / n, 6),
        "avg_output_tokens": round(toks / float(n), 1),
        "avg_quality": round(qual / n, 3),
        "total_cost_usd": round(cost, 4),
    }


def relative_delta(current, previous, key):
    a = current.get(key) or 0
    b = previous.get(key) or 0
    if b == 0:
        return None if a == 0 else 1.0
    return round((a - b) / float(b), 4)


def window_bounds(days=7, offset_days=0, now=None):
    end = (now or utc_now()) - timedelta(days=offset_days)
    start = end - timedelta(days=days)
    return start, end


def daily_series(rows, days=30, now=None):
    now = now or utc_now()
    buckets = {}  # type: Dict[str, Dict[str, Any]]
    for row in rows:
        day = row.timestamp.strftime("%Y-%m-%d")
        bucket = buckets.setdefault(
            day,
            {"date": day, "events": 0, "failed": 0, "cost_usd": 0.0, "latency_ms": 0.0, "factual_errors": 0},
        )
        bucket["events"] += 1
        if row.failed:
            bucket["failed"] += 1
        if "factual_error" in row.flags:
            bucket["factual_errors"] += 1
        bucket["cost_usd"] += row.cost_usd or 0
        bucket["latency_ms"] += row.latency_ms or 0

    series = []
    for i in range(days, -1, -1):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        bucket = buckets.get(
            day, {"date": day, "events": 0, "failed": 0, "cost_usd": 0.0, "latency_ms": 0.0, "factual_errors": 0}
        )
        n = bucket["events"]
        series.append(
            {
                "date": day,
                "events": n,
                "failure_rate": round(bucket["failed"] / float(n), 4) if n else 0,
                "factual_error_rate": round(bucket["factual_errors"] / float(n), 4) if n else 0,
                "cost_usd": round(bucket["cost_usd"], 4),
                "avg_latency_ms": round(bucket["latency_ms"] / n, 1) if n else 0,
            }
        )
    return series


def by_model(rows):
    grouped = defaultdict(
        lambda: {
            "model": "",
            "provider": "",
            "events": 0,
            "failed": 0,
            "cost_usd": 0.0,
            "latency_ms": 0.0,
            "quality": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "first": None,
            "last": None,
            "flag_counts": defaultdict(int),
        }
    )
    for row in rows:
        bucket = grouped[row.model]
        bucket["model"] = row.model
        bucket["provider"] = row.provider
        bucket["events"] += 1
        if row.failed:
            bucket["failed"] += 1
        bucket["cost_usd"] += row.cost_usd or 0
        bucket["latency_ms"] += row.latency_ms or 0
        bucket["quality"] += row.quality_score or 0
        bucket["prompt_tokens"] += row.prompt_tokens or 0
        bucket["completion_tokens"] += row.completion_tokens or 0
        if bucket["first"] is None or row.timestamp < bucket["first"]:
            bucket["first"] = row.timestamp
        if bucket["last"] is None or row.timestamp > bucket["last"]:
            bucket["last"] = row.timestamp
        for flag in row.flags:
            bucket["flag_counts"][flag] += 1
    return grouped


def model_rows(rows):
    models = []
    for bucket in by_model(rows).values():
        n = bucket["events"] or 1
        quality = bucket["quality"] / n
        avg_cost = bucket["cost_usd"] / n
        models.append(
            {
                "model": bucket["model"],
                "provider": bucket["provider"],
                "events": bucket["events"],
                "failure_rate": round(bucket["failed"] / float(bucket["events"]), 4) if bucket["events"] else 0,
                "total_cost_usd": round(bucket["cost_usd"], 4),
                "avg_cost_usd": round(avg_cost, 6),
                "avg_latency_ms": round(bucket["latency_ms"] / n, 1),
                "avg_quality": round(quality, 3),
                "cost_per_quality": round(avg_cost / max(quality, 0.05), 6),
                "prompt_tokens": bucket["prompt_tokens"],
                "completion_tokens": bucket["completion_tokens"],
                "first_seen": iso_z(bucket["first"]),
                "last_seen": iso_z(bucket["last"]),
            }
        )
    models.sort(key=lambda item: item["cost_per_quality"])
    return models
