from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Document
from app.services.rag import get_llm
from langchain.schema import HumanMessage, SystemMessage

router = APIRouter(prefix="/api", tags=["lessons"])


@router.get("/lessons-learned")
def lessons_learned(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = (
        db.query(Document)
        .filter(Document.doc_category.in_(["Incident Report", "Audit Report"]))
        .all()
    )
    if not docs:
        return {"common_failures": [], "preventive_suggestions": [], "lessons_learned": []}

    combined_text = "\n\n".join(
        f"[{d.filename}] {d.extracted_text_preview or ''}" for d in docs
    )[:8000]

    llm = get_llm()
    messages = [
        SystemMessage(content="You analyze industrial incident, near-miss, and audit reports. "
                               "Return three clearly labeled sections: 'Common Failures', "
                               "'Preventive Suggestions', and 'Lessons Learned', each as a short bullet list."),
        HumanMessage(content=combined_text),
    ]
    response = llm.invoke(messages)
    return {"analysis": response.content, "source_documents": [d.filename for d in docs]}
