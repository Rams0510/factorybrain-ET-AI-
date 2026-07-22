"""
Orchestrates the full System Flow described in the spec:

Detect File Type -> OCR (if scanned) -> Extract Text -> Parse Tables ->
Computer Vision (P&ID) -> Entity Extraction -> Store Metadata (MySQL) ->
Generate Embeddings -> Store in ChromaDB -> Build Knowledge Graph (Neo4j)
"""
import os
import tempfile
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Document, DocumentStatus, ExtractedEntity, Equipment
from app.services.file_detection import detect_file_type, pdf_is_scanned, classify_document_category
from app.services.ocr import ocr_pdf
from app.services.parsing import parse_pdf_text, parse_pdf_tables, parse_document
from app.services.cv_pid import analyze_pid_page, render_pdf_page_to_image
from app.services.entity_extraction import extract_entities
from app.services.embeddings import index_document_chunks, delete_document_vectors
from app.services import neo4j_service


def process_document(db: Session, document: Document, user_plant: str | None = None):
    try:
        document.status = DocumentStatus.PROCESSING
        document.error_message = None
        db.commit()

        # Idempotency: if this is a retry (Celery re-running after a
        # transient failure), clear any partial entity rows from the
        # previous attempt so we don't end up with duplicates. Equipment
        # upserts and ChromaDB upserts are already naturally idempotent.
        db.query(ExtractedEntity).filter(ExtractedEntity.document_id == document.id).delete()
        db.commit()

        file_type = detect_file_type(document.filename)
        document.file_type = file_type
        text = ""
        ocr_used = False
        pid_analysis = None

        if file_type == "pdf":
            if pdf_is_scanned(document.stored_path):
                text = ocr_pdf(document.stored_path)
                ocr_used = True
            else:
                text = parse_pdf_text(document.stored_path)

            category_preview = text[:800]
            category = classify_document_category(category_preview, document.filename)

            if category == "Engineering Drawing (P&ID)":
                with tempfile.TemporaryDirectory() as tmpdir:
                    img_path = os.path.join(tmpdir, "page0.png")
                    render_pdf_page_to_image(document.stored_path, 0, img_path)
                    pid_analysis = analyze_pid_page(img_path)

            # Table extraction merged into text for chunking/embedding
            tables = parse_pdf_tables(document.stored_path)
            for t in tables:
                rows_text = "\n".join(" | ".join(str(c) for c in row if c) for row in t["rows"] if row)
                text += f"\n\n[Table on page {t['page']}]\n{rows_text}"

        elif file_type in ("docx", "xlsx", "csv", "txt", "image"):
            text = parse_document(file_type, document.stored_path)
            category = classify_document_category(text[:800], document.filename)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        document.doc_category = category
        document.ocr_used = ocr_used
        document.extracted_text_preview = text[:1000]
        document.status = DocumentStatus.PARSED
        db.commit()

        # --- Entity extraction ---
        entities = extract_entities(text)
        for e in entities:
            db.add(ExtractedEntity(
                document_id=document.id,
                entity_type=e["entity_type"],
                entity_value=e["entity_value"],
                confidence_score=e["confidence_score"],
                context_snippet=e["context_snippet"],
            ))

        # Upsert Equipment rows in MySQL from EQUIPMENT_ID entities
        equipment_tags = {e["entity_value"] for e in entities if e["entity_type"] == "EQUIPMENT_ID"}
        for tag in equipment_tags:
            existing = db.query(Equipment).filter(Equipment.tag == tag).first()
            if not existing:
                db.add(Equipment(tag=tag, equipment_type="Unknown", plant=user_plant))

        # If CV found equipment on a P&ID page, merge those in too
        if pid_analysis:
            for item in pid_analysis.get("equipment", []):
                tag = item.get("tag")
                if tag:
                    existing = db.query(Equipment).filter(Equipment.tag == tag).first()
                    if not existing:
                        db.add(Equipment(tag=tag, equipment_type=item["type"].title(), plant=user_plant))

        db.commit()

        # --- Embeddings / ChromaDB ---
        chunk_count = index_document_chunks(document.id, document.filename, text)
        document.chunk_count = chunk_count

        # --- Neo4j knowledge graph ---
        neo4j_service.upsert_document_node(document.id, document.filename, category, user_plant)
        neo4j_service.upsert_equipment_from_entities(document.id, entities, user_plant)

        document.status = DocumentStatus.EMBEDDED
        document.processed_at = datetime.utcnow()
        db.commit()

    except Exception as exc:
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)
        db.commit()
        raise


def delete_document_everywhere(db: Session, document: Document):
    delete_document_vectors(document.id)
    try:
        if os.path.exists(document.stored_path):
            os.remove(document.stored_path)
    except OSError:
        pass
    db.delete(document)
    db.commit()
