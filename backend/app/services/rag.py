"""
Retrieval-Augmented Generation pipeline.

Flow: user question -> semantic_search (ChromaDB) -> build grounded prompt
-> Gemini 2.5 Flash (via langchain-google-genai) -> answer + citations +
confidence score derived from retrieval similarity.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.config import get_settings
from app.services.embeddings import semantic_search

settings = get_settings()

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
        )
    return _llm


SYSTEM_PROMPT = """You are FactoryBrain AI, an industrial engineering knowledge assistant.
You answer ONLY using the provided document excerpts (context). If the context does not
contain the answer, say clearly that the information was not found in the uploaded documents.
Always be precise about equipment tags, dates, pressures/temperatures, and safety requirements.
Cite which document each fact came from using the filename given in the context."""


def _distance_to_confidence(distance: float | None) -> float:
    """Cosine distance (0=identical, 2=opposite) -> a 0-1 confidence score."""
    if distance is None:
        return 0.5
    similarity = max(0.0, 1 - (distance / 2))
    return round(similarity, 3)


def answer_question(question: str) -> dict:
    hits = semantic_search(question)

    if not hits:
        return {
            "answer": "I couldn't find any relevant information in the uploaded documents for this question.",
            "confidence_score": 0.0,
            "sources": [],
        }

    context_blocks = []
    sources = []
    for h in hits:
        filename = h["metadata"].get("filename", "unknown")
        context_blocks.append(f"[Source: {filename}]\n{h['text']}")
        sources.append({
            "document_id": h["metadata"].get("document_id"),
            "filename": filename,
            "chunk_text": h["text"][:400],
            "score": _distance_to_confidence(h.get("distance")),
        })

    context_text = "\n\n---\n\n".join(context_blocks)

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"CONTEXT:\n{context_text}\n\nQUESTION: {question}"),
    ]
    response = llm.invoke(messages)

    avg_confidence = round(sum(s["score"] for s in sources) / len(sources), 3)

    return {
        "answer": response.content,
        "confidence_score": avg_confidence,
        "sources": sources,
    }
