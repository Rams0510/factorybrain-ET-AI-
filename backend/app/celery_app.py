"""
Celery app for background document processing at scale. Replaces the
earlier FastAPI BackgroundTasks approach, which ran jobs in-process with
no persistence, no retries, and no visibility — fine for a handful of
files, but not for thousands of documents / continuous ingestion.

Run the worker with:
    celery -A app.celery_app worker --loglevel=info --concurrency=4
(see docker-compose.yml's celery_worker service)
"""
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "factorybrain",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Report "started" so the frontend can distinguish queued vs running.
    task_track_started=True,
    # Only ack after the task finishes — if a worker dies mid-job, the task
    # goes back on the queue instead of being silently lost.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # One task at a time per worker process; document processing is
    # CPU/IO heavy (OCR, CV, embeddings) so we don't want a worker
    # grabbing a big backlog while a slow job is still running.
    worker_prefetch_multiplier=1,
    result_expires=86400,
)

celery_app.autodiscover_tasks(["app"])
