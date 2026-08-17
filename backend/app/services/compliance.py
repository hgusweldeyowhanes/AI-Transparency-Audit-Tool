from collections import defaultdict
from html import escape

from ..clock import iso_z, utc_now
from ..config import settings
from ..repositories import EventStore
from .analytics import model_rows


def inventory(db):
    rows = EventStore(db).all()
    flag_counts = defaultdict(int)
    oldest = newest = None
    for row in rows:
        if oldest is None or row.timestamp < oldest:
            oldest = row.timestamp
        if newest is None or row.timestamp > newest:
            newest = row.timestamp
        for flag in row.flags:
            flag_counts[flag] += 1
    return {
        "event_count": len(rows),
        "models": model_rows(rows),
        "failure_counts": dict(flag_counts),
        "oldest_event": iso_z(oldest),
        "newest_event": iso_z(newest),
        "retention_days": settings.retention_days,
    }


def eu_ai_act_payload(db):
    return {
        "title": "EU AI Act logging pack (template)",
        "disclaimer": (
            "This is an engineering template mapped to record-keeping themes in the EU AI Act "
            "(notably logging / traceability for high-risk systems). It is not legal advice "
            "and does not certify conformity."
        ),
        "generated_at": iso_z(utc_now()),
        "articles_referenced": [
            {
                "ref": "Art. 12 — Record-keeping",
                "how_we_help": "Immutable-style event log of prompts, completions, model IDs, timestamps, and failure flags.",
            },
            {
                "ref": "Art. 13 — Transparency",
                "how_we_help": "Model inventory, quality scores, and human-readable failure taxonomy for operators.",
            },
            {
                "ref": "Art. 14 — Human oversight",
                "how_we_help": "Search + incident detection so a human can inspect and roll back a prompt version.",
            },
        ],
        "inventory": inventory(db),
        "retention_policy": {
            "stated_days": settings.retention_days,
            "note": "Free self-hosted default is 30 days (GTM free tier). Raise this for regulated workloads.",
        },
    }


def sec_payload(db):
    return {
        "title": "SEC AI disclosure pack (template)",
        "disclaimer": (
            "Template for internal evidence rooms preparing AI-related disclosures. "
            "Not a filing, not legal advice, and not an SEC form."
        ),
        "generated_at": iso_z(utc_now()),
        "sections": [
            {
                "heading": "System inventory",
                "body": "Models in production during the window, with volume and observed failure rates.",
            },
            {
                "heading": "Quality monitoring",
                "body": "Heuristic detectors for empty output, refusals, ungrounded citations, and PII-like strings.",
            },
            {
                "heading": "Change control",
                "body": "prompt_version is logged on every event so a regression can be tied to a specific change.",
            },
        ],
        "inventory": inventory(db),
    }


def render_html(title, disclaimer, payload):
    models = payload.get("inventory", {}).get("models", [])
    models_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{:.1%}</td></tr>".format(
            escape(m["model"]),
            escape(m["provider"]),
            m["events"],
            m["failure_rate"],
        )
        for m in models
    )
    flags = payload.get("inventory", {}).get("failure_counts", {})
    flag_rows = "".join(
        "<tr><td>{}</td><td>{}</td></tr>".format(escape(k), v) for k, v in sorted(flags.items())
    )
    articles = payload.get("articles_referenced") or payload.get("sections") or []
    art_html = "".join(
        "<li><strong>{}</strong> — {}</li>".format(
            escape(a.get("ref") or a.get("heading") or ""),
            escape(a.get("how_we_help") or a.get("body") or ""),
        )
        for a in articles
    )
    inv = payload.get("inventory", {})
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>{title}</title>
<style>
  body {{ font-family: "Iowan Old Style", Georgia, serif; background:#070b14; color:#e2e8f0; margin:0; padding:48px; }}
  h1 {{ font-weight: 500; letter-spacing: -0.02em; }}
  .seal {{ color:#2dd4bf; font-size:12px; letter-spacing:0.16em; text-transform:uppercase; }}
  .disc {{ color:#94a3b8; font-size:14px; max-width:720px; }}
  table {{ border-collapse: collapse; width:100%; margin:24px 0; font-family: ui-sans-serif, system-ui; font-size:14px; }}
  th, td {{ border-bottom:1px solid #1e293b; text-align:left; padding:8px 10px; }}
  th {{ color:#94a3b8; font-weight:500; }}
</style></head>
<body>
  <div class="seal">audit-ai · compliance template</div>
  <h1>{title}</h1>
  <p class="disc">{disclaimer}</p>
  <p>Generated {generated}. Events: {events}. Retention: {retention} days.</p>
  <h2>Mapped controls</h2>
  <ul>{articles}</ul>
  <h2>Model inventory</h2>
  <table><thead><tr><th>Model</th><th>Provider</th><th>Events</th><th>Failure rate</th></tr></thead>
  <tbody>{models}</tbody></table>
  <h2>Failure flags</h2>
  <table><thead><tr><th>Flag</th><th>Count</th></tr></thead>
  <tbody>{flags}</tbody></table>
</body></html>
""".format(
        title=escape(title),
        disclaimer=escape(disclaimer),
        generated=escape(payload.get("generated_at") or ""),
        events=inv.get("event_count", 0),
        retention=inv.get("retention_days", settings.retention_days),
        articles=art_html,
        models=models_rows or "<tr><td colspan=4>No events</td></tr>",
        flags=flag_rows or "<tr><td colspan=2>None</td></tr>",
    )
