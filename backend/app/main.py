from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_analytics, routes_analyze, routes_knowledge, routes_leads, routes_notify
from app.db import Base, engine
from app.models import db_models  # noqa: F401  (registers models on Base)

app = FastAPI(
    title="AI Business Operations Hub",
    description="Autonomous intake -> classification -> RAG -> action pipeline.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(routes_analyze.router)
app.include_router(routes_knowledge.router)
app.include_router(routes_leads.router)
app.include_router(routes_analytics.router)
app.include_router(routes_notify.router)
