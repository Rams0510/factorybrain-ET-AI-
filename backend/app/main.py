from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app import models  # noqa: F401 ensures models are registered before create_all
from app.routers import auth, documents, equipment, chat, analytics, graph, maintenance, compliance, search, lessons

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates MySQL tables if they don't already exist. For production
    # schema evolution, switch to Alembic migrations (scaffold included).
    Base.metadata.create_all(bind=engine)
    try:
        from app.services.neo4j_service import ensure_constraints
        ensure_constraints()
    except Exception as exc:
        # Neo4j may not be reachable yet on first boot in docker-compose;
        # constraints will be (re)applied on next successful startup.
        print(f"[startup] Neo4j constraint setup deferred: {exc}")


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(equipment.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(graph.router)
app.include_router(maintenance.router)
app.include_router(compliance.router)
app.include_router(search.router)
app.include_router(lessons.router)
