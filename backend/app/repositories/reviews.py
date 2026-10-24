from sqlalchemy.orm import Session

from ..models import OversightReview


class ReviewStore:
    def __init__(self, db):
        # type: (Session) -> None
        self.db = db

    def newest_first(self):
        return (
            self.db.query(OversightReview)
            .order_by(OversightReview.created_at.desc(), OversightReview.id.desc())
            .all()
        )

    def for_event(self, event_id):
        return (
            self.db.query(OversightReview)
            .filter(OversightReview.event_id == event_id)
            .order_by(OversightReview.created_at.desc(), OversightReview.id.desc())
            .all()
        )
