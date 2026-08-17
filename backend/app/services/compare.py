from ..repositories import EventStore
from .analytics import model_rows, window_bounds


def compare_models(db, days=30):
    start, _end = window_bounds(days, 0)
    rows = EventStore(db).since(start)
    return {"days": days, "models": model_rows(rows)}
