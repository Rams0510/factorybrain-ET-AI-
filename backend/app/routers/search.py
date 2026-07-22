from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Document, Equipment, ExtractedEntity, MaintenanceRecord, InspectionRecord
from app.services.embeddings import semantic_search

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def global_search(
    q: str,
    semantic: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if semantic:
        hits = semantic_search(q, top_k=10)
        return {"mode": "semantic", "results": hits}

    like = f"%{q}%"
    documents = db.query(Document).filter(Document.filename.ilike(like)).limit(20).all()
    equipment = db.query(Equipment).filter(Equipment.tag.ilike(like)).limit(20).all()
    engineers = (
        db.query(ExtractedEntity)
        .filter(ExtractedEntity.entity_type == "ENGINEER", ExtractedEntity.entity_value.ilike(like))
        .limit(20)
        .all()
    )
    plants = db.query(Equipment.plant).filter(Equipment.plant.ilike(like)).distinct().limit(20).all()

    return {
        "mode": "keyword",
        "documents": [{"id": d.id, "filename": d.filename, "category": d.doc_category} for d in documents],
        "equipment": [{"tag": e.tag, "type": e.equipment_type, "plant": e.plant} for e in equipment],
        "engineers": [{"name": e.entity_value, "document_id": e.document_id} for e in engineers],
        "plants": [p[0] for p in plants if p[0]],
    }
