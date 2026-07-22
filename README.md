# FactoryBrain AI

**Industrial Knowledge Intelligence Platform** — upload maintenance
reports, SOPs, safety manuals, P&ID drawings, inspection/audit reports and
ask an AI assistant questions about your plant, grounded in your own
documents via Retrieval-Augmented Generation (RAG).

> Wired to real cloud services — Firebase Authentication and Google
> Gemini are required (not mocked). See **[Installation Guide](docs/INSTALLATION.md)**
> for how to provision them before running `docker-compose up`.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, React Router, React Query, Framer Motion, Recharts |
| Backend | FastAPI, SQLAlchemy, Pydantic, Uvicorn |
| Auth | Firebase Authentication (Google + Email) |
| Database | MySQL |
| Knowledge Graph | Neo4j |
| Vector Database | ChromaDB |
| LLM | Google Gemini 2.5 Flash |
| AI Framework | LangChain |
| OCR | Tesseract |
| Computer Vision | OpenCV (heuristic P&ID shape/tag detection) |
| Document Parsing | PyMuPDF, pdfplumber, python-docx, openpyxl |
| Deployment | Docker, Docker Compose |

## Quick Start

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
mkdir -p backend/secrets   # place firebase-service-account.json here
docker-compose up --build
```

Then open http://localhost:5173. See **[docs/INSTALLATION.md](docs/INSTALLATION.md)**
for the full Firebase/Gemini/Neo4j setup walkthrough — the app will not
authenticate or answer chat questions until those keys are in place.

Once running, upload the files in `sample_data/` to see the full pipeline
in action (see `sample_data/README.md`).

## Project Structure

```
factorybrain/
  backend/           FastAPI app: routers, services (OCR, CV, RAG, entity
                      extraction, Neo4j, ChromaDB), SQLAlchemy models
  frontend/          React + TypeScript + Vite SPA
  database/          MySQL schema.sql
  docker/            (reserved for extra deployment configs)
  docs/              Architecture, DB schema, knowledge graph, installation
  sample_data/       Ready-to-upload sample industrial documents
  docker-compose.yml Orchestrates mysql, neo4j, chromadb, backend, frontend
```

## System Flow

Upload → Detect File Type → OCR (if scanned) → Extract Text → Parse Tables
→ Computer Vision (P&ID) → Entity Extraction → Store Metadata (MySQL) →
Generate Embeddings → Store in ChromaDB → Build Knowledge Graph (Neo4j) →
RAG Pipeline → Gemini → Answer with Source Citations.

Full diagrams: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Modules

- **Authentication** — Firebase Google + Email login, protected routes
- **Dashboard** — documents, equipment, compliance score, maintenance alerts, charts
- **Document Upload** — drag & drop, multi-file, live status polling
- **OCR** — automatic scanned-PDF detection + Tesseract extraction
- **Document Parsing** — PDF/DOCX/XLSX/CSV/TXT
- **Computer Vision** — OpenCV heuristic P&ID pipe/pump/valve/tank/tag detection
- **Entity Extraction** — equipment IDs, engineers, pressures, temperatures, dates, failure reasons, safety rules, regulatory references, locations, with confidence scores
- **MySQL** — users, documents, equipment, metadata, chat history, notifications, maintenance/inspection records
- **Neo4j Knowledge Graph** — Equipment/Engineer/Document/Incident/Plant nodes with CONNECTED_TO/FAILED_DUE_TO/MAINTAINED_BY/MENTIONED_IN/LOCATED_AT/GENERATED_FROM relationships
- **ChromaDB** — chunking, Gemini embeddings, semantic search
- **Industrial AI Chat** — RAG-grounded Q&A with confidence score + source citations
- **Maintenance Intelligence** — root cause analysis, recommendations, risk score, failure-window prediction
- **Compliance Intelligence** — Factory Act / OISD / PESO / ISO / Environmental checks, missing reports, expired-certificate flags
- **Lessons Learned** — Gemini-summarized incident/near-miss/audit analysis
- **Analytics** — document/equipment/maintenance/compliance/failure trend charts
- **Search** — global keyword search + semantic (vector) search

## API Reference

| Method | Path | Description |
|---|---|---|
| POST | `/api/login` | Verify Firebase ID token, upsert user |
| GET | `/api/me` | Current authenticated user |
| POST | `/api/upload` | Multi-file upload, triggers background processing pipeline |
| GET | `/api/documents` | List documents (filter by category/search) |
| GET | `/api/documents/{id}` | Document detail |
| DELETE | `/api/document/{id}` | Delete document + vectors |
| GET | `/api/equipment` | List equipment (filter by type/plant) |
| POST | `/api/chat` | RAG-powered chat |
| GET | `/api/chat/history/{session_id}` | Chat history for a session |
| GET | `/api/analytics` | Dashboard/analytics aggregates |
| GET | `/api/graph` | Neo4j knowledge graph (nodes + edges) |
| GET | `/api/maintenance` | Maintenance insights (risk score, RCA, recommendations) |
| GET | `/api/maintenance/{tag}/ai-analysis` | Gemini-generated narrative RCA |
| GET | `/api/compliance` | Compliance report |
| GET | `/api/search` | Global keyword or semantic search |
| GET | `/api/lessons-learned` | Incident/audit pattern analysis |

Interactive Swagger docs: `http://localhost:8000/docs` once running.

## Notes on Scope

- The **Computer Vision** module uses a real, explainable OpenCV heuristic
  pipeline (Hough line/circle detection + contour analysis + OCR tag
  reading) rather than a trained object-detection model — see
  `backend/app/services/cv_pid.py` for the documented rationale and how to
  swap in a trained model later without changing the calling contract.
- **Entity extraction** uses tuned regex/rule patterns rather than a
  trained NER model, keeping the system dependency-light while still
  producing real, usable structured data with confidence scores.
- Archive (`.zip`) and email-export (`.eml`/`.msg`) uploads are accepted by
  the file-type detector; wire in `zipfile`/`email` extraction in
  `app/services/parsing.py` if you need those formats processed rather
  than just stored.
