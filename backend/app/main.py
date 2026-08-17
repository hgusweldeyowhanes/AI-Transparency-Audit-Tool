from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine, SessionLocal
from .routers import compare, drift, events, failures, metrics, reports, trial
from .seed import seed_if_empty

app = FastAPI(
    title="audit-ai",
    description="Open-source, LLM-native audit trail for regulatory compliance.",
    version="0.1.0",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(metrics.router)
app.include_router(drift.router)
app.include_router(failures.router)
app.include_router(compare.router)
app.include_router(reports.router)
app.include_router(trial.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "product": "audit-ai"}
