from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.database.init_db import init_db
from backend.routes import auth, complaint, dashboard
from backend.services import celery_tasks  # noqa: F401
from backend.services.classifier import warmup_classifier
from backend.services.observability import (
    app_logger,
    configure_logging,
    metrics,
    request_metrics_middleware,
)
from backend.services.queue import start_worker, stop_worker
from backend.services.rag import warmup_generator


app = FastAPI(title="Grievance AI System")
configure_logging()

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(request_metrics_middleware)


@app.on_event("startup")
def startup() -> None:
    app_logger.info("application_starting")
    init_db()
    warmup_classifier()
    warmup_generator()
    start_worker()
    metrics.set_gauge("app.started", 1)
    app_logger.info("application_started")


@app.on_event("shutdown")
def shutdown() -> None:
    app_logger.info("application_stopping")
    stop_worker()
    metrics.set_gauge("app.started", 0)
    app_logger.info("application_stopped")


app.include_router(auth.router)
app.include_router(complaint.router)
app.include_router(dashboard.router)
