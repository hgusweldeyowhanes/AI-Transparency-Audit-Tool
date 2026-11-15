from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .migrate import migrate_schema
from .routers import register_routes
from .seed import seed_if_empty
from .services.chain import backfill_chain
from .services.judge import ensure_default_rubric
from .services.incidents import seed_demo_incident
from .services.registry import seed_registry


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_schema()
    db = SessionLocal()
    try:
        ensure_default_rubric(db)
        seed_registry(db)
        seed_demo_incident(db)
        seed_if_empty(db)
        backfill_chain(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="audit-ai",
    description="Open-source, LLM-native audit trail for regulatory compliance.",
    version="0.2.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_routes(app)


@app.get("/health")
def health():
    return {"status": "ok", "product": "audit-ai", "version": "0.2.0"}
