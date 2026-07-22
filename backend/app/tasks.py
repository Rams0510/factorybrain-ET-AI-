"""
Celery task entry point for document processing. This is what the upload
endpoint enqueues instead of running work in-process.
"""
import traceback
from celery.utils.log import get_task_logger

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Document
from app.services.pipeline import process_document

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.process_document_task",
    autoretry_for=(Exception,),
    retry_backoff=True,       # exponential backoff between retries
    retry_backoff_max=300,    # cap backoff at 5 minutes
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def process_document_task(self, document_id: str, user_plant: str | None = None):
    """
    Opens its own DB session (never reuse a request-scoped session in a
    background job — see prior fix). Retries automatically on any
    exception (transient Gemini/Neo4j/Chroma/MySQL errors) with
    exponential backoff, up to 5 attempts, before the document is left in
    FAILED status for manual review.
    """
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            logger.warning(f"Document {document_id} not found — skipping")
            return
        document.task_id = self.request.id
        db.commit()
        process_document(db, document, user_plant)
        logger.info(f"Document {document_id} processed successfully")
    except Exception:
        logger.error(f"Error processing document {document_id} "
                      f"(attempt {self.request.retries + 1}):\n{traceback.format_exc()}")
        raise
    finally:
        db.close()
