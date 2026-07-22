# Installation Guide

FactoryBrain AI is wired to real cloud services (Firebase Authentication,
Google Gemini, and optionally Neo4j Aura) rather than local stand-ins, so
before running `docker-compose up` you need to provision three things.

## 1. Firebase Authentication

1. Go to https://console.firebase.google.com and create a project.
2. **Authentication -> Sign-in method**: enable **Google** and **Email/Password**.
3. **Project settings -> General -> Your apps**: create a Web app and copy the config into `.env` at the repo root (copy `.env.example` -> `.env` first). These become `VITE_FIREBASE_*` and are baked into the frontend at build time.
4. **Project settings -> Service accounts**: click "Generate new private key". Save the downloaded JSON as `backend/secrets/firebase-service-account.json`.
5. In `backend/.env` (copy from `backend/.env.example`), set `FIREBASE_PROJECT_ID` to your project ID.

## 2. Google Gemini API

1. Get an API key at https://aistudio.google.com/app/apikey.
2. Set `GOOGLE_API_KEY` in `backend/.env`.

## 3. Neo4j

**Option A — self-hosted (default, zero extra setup):** the bundled
`docker-compose.yml` already runs a Neo4j container; no changes needed.

**Option B — Neo4j Aura (managed cloud):**
1. Create a free instance at https://neo4j.com/cloud/aura/.
2. In `backend/.env`, set:
   ```
   NEO4J_URI=neo4j+s://<your-db-id>.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your-generated-password>
   ```
3. Remove or comment out the `neo4j` service block in `docker-compose.yml` and the `depends_on: neo4j` entry under `backend` (optional — the self-hosted container can simply sit unused).

## 4. MySQL

The bundled `mysql` service works out of the box with the credentials in
`backend/.env.example`. For a managed MySQL (RDS, Cloud SQL, PlanetScale),
update `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` in
`backend/.env` and remove the `mysql` service from `docker-compose.yml`.

## 5. Run it

```bash
cp .env.example .env                       # Firebase web config (build-time)
cp backend/.env.example backend/.env       # server-side secrets
cp frontend/.env.example frontend/.env     # optional, for local `npm run dev`
mkdir -p backend/secrets
# place your firebase-service-account.json inside backend/secrets/

docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- ChromaDB: http://localhost:8001

## 6. Local (non-Docker) development

Backend:
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# requires local tesseract-ocr binary installed on your OS
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

- **401 on every API call**: the Firebase ID token isn't being verified —
  confirm `backend/secrets/firebase-service-account.json` exists and
  `FIREBASE_PROJECT_ID` matches.
- **Chat returns "couldn't find any relevant information"**: no documents
  have finished processing yet — check `GET /api/documents` for `status`.
- **Gemini errors (401/403)**: check `GOOGLE_API_KEY` and that the Gemini
  API is enabled for your Google Cloud project/API key.
- **Neo4j connection refused on first boot**: the backend retries
  constraint setup on next startup; this is expected on the very first
  `docker-compose up` while Neo4j is still initializing.
