# FactoryBrain AI — Architecture

## System Flow

```mermaid
flowchart TD
    A[User Login - Firebase Auth] --> B[Upload Documents]
    B --> C[Detect File Type]
    C --> D{Scanned?}
    D -- Yes --> E[OCR - Tesseract]
    D -- No --> F[Extract Text - PyMuPDF/pdfplumber/docx/openpyxl]
    E --> G[Parse Tables]
    F --> G
    G --> H[Computer Vision - OpenCV P&ID heuristics]
    H --> I[Entity Extraction - regex/NER rules]
    I --> J[(MySQL - metadata, equipment, records)]
    I --> K[Generate Embeddings - Gemini text-embedding-004]
    K --> L[(ChromaDB - vector store)]
    I --> M[(Neo4j - knowledge graph)]
    J --> N[RAG Pipeline - LangChain]
    L --> N
    M --> N
    N --> O[Gemini 2.5 Flash]
    O --> P[AI Response + Source Citations]
```

## Component Overview

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React 19 + TypeScript + Vite + Tailwind | UI, auth flows, dashboards, chat |
| Auth | Firebase Authentication | Google + Email login, ID token issuance |
| API | FastAPI | REST endpoints, orchestration |
| Relational DB | MySQL | Users, documents, equipment, records, chat history |
| Vector DB | ChromaDB | Semantic search over document chunks |
| Graph DB | Neo4j | Equipment/Engineer/Document relationship graph |
| LLM | Gemini 2.5 Flash | RAG answer generation, root-cause analysis |
| OCR | Tesseract | Scanned document text extraction |
| CV | OpenCV | P&ID heuristic shape/tag detection |
| Orchestration | Docker Compose | Local/prod multi-service deployment |

## Request Flow: AI Chat

1. Frontend sends `POST /api/chat` with a Firebase ID token (Bearer auth) and the user's question.
2. Backend verifies the token via `firebase-admin`, resolves/creates the MySQL `User` row.
3. `app/services/rag.py` embeds the question (Gemini embeddings) and queries ChromaDB for the top-K most similar chunks.
4. Retrieved chunks + filenames are assembled into a grounded prompt and sent to Gemini 2.5 Flash via LangChain.
5. The response, confidence score (derived from retrieval similarity), and source citations are stored in `chat_history` and returned to the frontend.

## Deployment Topology

```mermaid
graph LR
    subgraph Docker Compose
        FE[frontend :5173] --> BE[backend :8000]
        BE --> MYSQL[(mysql :3306)]
        BE --> NEO4J[(neo4j :7687/7474)]
        BE --> CHROMA[(chromadb :8001)]
        BE --> GEMINI[[Gemini API - external]]
        BE --> FIREBASE[[Firebase Auth - external]]
    end
```
