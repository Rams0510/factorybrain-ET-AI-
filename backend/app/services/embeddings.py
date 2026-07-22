"""
Chunking, embedding (Google Gemini text-embedding-004), and storage/query
against a ChromaDB server (HttpClient — see docker-compose 'chromadb'
service). This is the vector layer of the RAG pipeline.
"""
import time
import random
import google.generativeai as genai
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.GOOGLE_API_KEY)

_chroma_client = None
_collection = None


def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _collection = _chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_len:
            break
        start = end - overlap
    return chunks


def embed_texts(texts: list[str], task_type: str = "retrieval_document", batch_size: int = 100) -> list[list[float]]:
    """
    Embeds many chunks with as few Gemini API calls as possible. The
    previous version called the API once PER CHUNK — fine for a handful
    of test documents, but at continuous-ingestion scale (thousands of
    documents, each split into many chunks) that means thousands of
    sequential network round-trips per document. Batching cuts that by
    ~100x and dramatically reduces exposure to per-minute rate limits.
    """
    all_vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        all_vectors.extend(_embed_batch_with_retry(batch, task_type))
    return all_vectors


def _embed_batch_with_retry(batch: list[str], task_type: str, max_retries: int = 5) -> list[list[float]]:
    """
    Retries with exponential backoff + jitter on transient failures
    (rate limits, brief API outages) — essential once upload volume is
    high enough to regularly hit per-minute quotas.
    """
    delay = 2.0
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            result = genai.embed_content(
                model=settings.GEMINI_EMBEDDING_MODEL,
                content=batch,
                task_type=task_type,
            )
            embedding = result["embedding"]
            # The SDK returns a flat vector for single-string content but
            # a list of vectors when content is a list — normalize here.
            if embedding and isinstance(embedding[0], (int, float)):
                embedding = [embedding]
            return embedding
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries - 1:
                break
            wait = delay + random.uniform(0, delay * 0.5)
            print(f"[embeddings] Batch embed failed (attempt {attempt + 1}/{max_retries}): {exc}. "
                  f"Retrying in {wait:.1f}s...")
            time.sleep(wait)
            delay = min(delay * 2, 60)
    raise last_exc


def index_document_chunks(document_id: str, filename: str, text: str) -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0

    vectors = embed_texts(chunks, task_type="retrieval_document")
    ids = [f"{document_id}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]

    collection = get_chroma_collection()
    collection.upsert(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas)
    return len(chunks)


def semantic_search(query: str, top_k: int = None) -> list[dict]:
    top_k = top_k or settings.TOP_K
    query_vector = embed_texts([query], task_type="retrieval_query")[0]
    collection = get_chroma_collection()
    results = collection.query(query_embeddings=[query_vector], n_results=top_k)

    output = []
    if results and results.get("ids"):
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
    return output


def delete_document_vectors(document_id: str):
    collection = get_chroma_collection()
    collection.delete(where={"document_id": document_id})
