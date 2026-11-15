"""Lightweight SQLite column/table upgrades for existing MVP databases."""

from __future__ import annotations

from sqlalchemy import inspect, text

from .database import engine


EVENT_COLUMNS = {
    "judge_rubric_version": "VARCHAR(64)",
    "judge_scores": "TEXT",
    "groundedness_score": "FLOAT",
    "prev_hash": "VARCHAR(64)",
    "event_hash": "VARCHAR(64)",
    "chain_index": "INTEGER",
    "purged_at": "DATETIME",
}


def migrate_schema() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "audit_events" in tables:
        existing = {c["name"] for c in inspector.get_columns("audit_events")}
        with engine.begin() as conn:
            for name, ddl in EVENT_COLUMNS.items():
                if name not in existing:
                    conn.execute(text("ALTER TABLE audit_events ADD COLUMN %s %s" % (name, ddl)))
