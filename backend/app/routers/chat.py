import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, ChatMessage
from app.schemas import ChatRequest, ChatResponse, SourceRef
from app.services.rag import answer_question

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session_id = payload.session_id or str(uuid.uuid4())

    # store user message
    db.add(ChatMessage(user_id=current_user.id, session_id=session_id, role="user", message=payload.message))
    db.commit()

    result = answer_question(payload.message)

    db.add(ChatMessage(
        user_id=current_user.id,
        session_id=session_id,
        role="assistant",
        message=result["answer"],
        sources=result["sources"],
        confidence_score=result["confidence_score"],
    ))
    db.commit()

    return ChatResponse(
        session_id=session_id,
        answer=result["answer"],
        confidence_score=result["confidence_score"],
        sources=[SourceRef(**s) for s in result["sources"]],
    )


@router.get("/chat/history/{session_id}")
def chat_history(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "role": m.role,
            "message": m.message,
            "sources": m.sources,
            "confidence_score": m.confidence_score,
            "created_at": m.created_at,
        }
        for m in messages
    ]
