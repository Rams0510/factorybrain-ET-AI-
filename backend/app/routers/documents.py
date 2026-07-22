import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Document, DocumentStatus
from app.schemas import DocumentOut, UploadResponse
from app.services.pipeline import delete_document_everywhere
from app.tasks import process_document_task
from app.celery_app import celery_app
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["documents"])
settings = get_settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

MAX_PAGE_SIZE = 200


@router.post("/upload", response_model=UploadResponse)
def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploaded_docs = []

    for file in files:
        ext = os.path.splitext(file.filename)[1]
        stored_name = f"{uuid.uuid4()}{ext}"
        stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)

        # Stream the upload to disk in chunks rather than reading the
        # entire file into memory with file.file.read() — matters once
        # files get into the tens/hundreds of MB range or many uploads
        # are happening concurrently.
        with open(stored_path, "wb") as f:
            shutil.copyfileobj(file.file, f, length=1024 * 1024)
        size_bytes = os.path.getsize(stored_path)

        document = Document(
            owner_id=current_user.id,
            filename=file.filename,
            stored_path=stored_path,
            size_bytes=size_bytes,
            status=DocumentStatus.UPLOADED,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Enqueue onto Celery/Redis instead of running in-process. This
        # survives backend restarts, retries transient failures with
        # backoff, and scales to many concurrent uploads by adding more
        # celery_worker replicas rather than blocking request threads.
        task = process_document_task.delay(document.id, current_user.plant)
        document.task_id = task.id
        db.commit()

        uploaded_docs.append(document)

    return UploadResponse(uploaded=[DocumentOut.model_validate(d) for d in uploaded_docs])


@router.get("/documents", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: str | None = None,
    search: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
):
    """
    Paginated by default (50 per page, capped at 200) — with continuous
    ingestion pushing document counts into the thousands, returning
    everything unbounded would get slow and heavy fast.
    """
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    if category:
        query = query.filter(Document.doc_category == category)
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    if status:
        query = query.filter(Document.status == status)
    return (
        query.order_by(Document.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/documents/count")
def count_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: str | None = None,
    search: str | None = None,
    status: str | None = None,
):
    """Total count for the current filters, so the frontend can paginate."""
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    if category:
        query = query.filter(Document.doc_category == category)
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    if status:
        query = query.filter(Document.status == status)
    return {"count": query.count()}


@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/documents/{document_id}/task-status")
def get_document_task_status(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Live Celery task state (PENDING/STARTED/RETRY/SUCCESS/FAILURE) for a
    document's processing job — more granular than the document's own
    status field, useful for showing retry counts on large batch uploads.
    """
    doc = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.task_id:
        return {"task_id": None, "state": "UNKNOWN"}

    result = celery_app.AsyncResult(doc.task_id)
    return {
        "task_id": doc.task_id,
        "state": result.state,
    }


@router.delete("/document/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document_everywhere(db, doc)
    return {"deleted": True, "document_id": document_id}
