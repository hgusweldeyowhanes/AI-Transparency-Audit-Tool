import re
from datetime import timedelta
from typing import List, Tuple

from sqlalchemy.orm import Session

from ..clock import utc_now
from ..models import AuditEvent

_SAFE_TOKEN = re.compile(r"^[a-zA-Z0-9._:-]+$")


class EventStore:
    def __init__(self, db):
        # type: (Session) -> None
        self.db = db

    def get(self, event_id):
        return self.db.query(AuditEvent).filter(AuditEvent.id == event_id).first()

    def count(self):
        return self.db.query(AuditEvent).count()

    def recent_baselines(self, limit=80):
        rows = (
            self.db.query(AuditEvent.latency_ms, AuditEvent.completion_tokens)
            .order_by(AuditEvent.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [r[0] for r in rows], [r[1] for r in rows]

    def since(self, start):
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.timestamp >= start)
            .order_by(AuditEvent.timestamp.asc())
            .all()
        )

    def between(self, start, end):
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.timestamp >= start, AuditEvent.timestamp < end)
            .all()
        )

    def latest(self, limit=2000):
        return self.db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()

    def all(self):
        return self.db.query(AuditEvent).all()

    def search(
        self,
        q=None,
        model=None,
        flag=None,
        tag=None,
        prompt_version=None,
        since=None,
        until=None,
        limit=50,
        offset=0,
    ):
        # type: (...) -> Tuple[int, List[AuditEvent]]
        query = self.db.query(AuditEvent)
        if model:
            query = query.filter(AuditEvent.model == model)
        if prompt_version:
            query = query.filter(AuditEvent.prompt_version == prompt_version)
        if since:
            query = query.filter(AuditEvent.timestamp >= since)
        if until:
            query = query.filter(AuditEvent.timestamp <= until)
        if q:
            like = "%" + q + "%"
            query = query.filter(
                (AuditEvent.prompt.like(like))
                | (AuditEvent.completion.like(like))
                | (AuditEvent.id.like(like))
            )
        if flag and _SAFE_TOKEN.match(flag):
            query = query.filter(AuditEvent.failure_flags.like('%"' + flag + '"%'))
        if tag and _SAFE_TOKEN.match(tag):
            query = query.filter(AuditEvent.tags.like('%"' + tag + '"%'))

        total = query.count()
        rows = query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()
        return total, rows


def days_ago(days, now=None):
    return (now or utc_now()) - timedelta(days=days)
