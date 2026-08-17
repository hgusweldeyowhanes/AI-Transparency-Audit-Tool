from fastapi import FastAPI

from . import compare, drift, events, failures, metrics, reports, trial

ROUTERS = (
    events.router,
    metrics.router,
    drift.router,
    failures.router,
    compare.router,
    reports.router,
    trial.router,
)


def register_routes(app):
    # type: (FastAPI) -> None
    for router in ROUTERS:
        app.include_router(router)
