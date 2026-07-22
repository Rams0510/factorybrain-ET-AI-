# Database Schema — MySQL

Full DDL lives in `database/schema.sql` and is mirrored by the SQLAlchemy
models in `backend/app/models.py` (the backend calls `create_all()` on
startup, so the two never drift as long as both are updated together).

## Entity-Relationship Overview

```mermaid
erDiagram
    USERS ||--o{ DOCUMENTS : uploads
    USERS ||--o{ CHAT_HISTORY : sends
    USERS ||--o{ NOTIFICATIONS : receives
    DOCUMENTS ||--o{ EXTRACTED_ENTITIES : yields
    DOCUMENTS ||--o{ MAINTENANCE_RECORDS : source_of
    DOCUMENTS ||--o{ INSPECTION_RECORDS : source_of
    DOCUMENTS ||--o{ COMPLIANCE_RECORDS : evidences
    EQUIPMENT ||--o{ MAINTENANCE_RECORDS : has
    EQUIPMENT ||--o{ INSPECTION_RECORDS : has

    USERS {
        string id PK
        string firebase_uid
        string email
        string role
        string department
        string plant
    }
    DOCUMENTS {
        string id PK
        string owner_id FK
        string filename
        string doc_category
        string status
        int chunk_count
    }
    EQUIPMENT {
        string id PK
        string tag
        string equipment_type
        string plant
        float risk_score
    }
    EXTRACTED_ENTITIES {
        string id PK
        string document_id FK
        string entity_type
        string entity_value
        float confidence_score
    }
    MAINTENANCE_RECORDS {
        string id PK
        string equipment_id FK
        string document_id FK
        text failure_reason
        float downtime_hours
    }
    INSPECTION_RECORDS {
        string id PK
        string equipment_id FK
        string document_id FK
        text findings
        string severity
    }
    CHAT_HISTORY {
        string id PK
        string user_id FK
        string session_id
        string role
        json sources
    }
    COMPLIANCE_RECORDS {
        string id PK
        string document_id FK
        string standard
        string status
    }
    NOTIFICATIONS {
        string id PK
        string user_id FK
        string level
        boolean is_read
    }
```

## Table Notes

- **users** — synced from Firebase on every successful login (`firebase_uid` is the join key).
- **documents** — one row per uploaded file; `status` tracks pipeline progress (`uploaded -> processing -> parsed -> embedded`, or `failed`).
- **extracted_entities** — generic entity table (equipment IDs, engineers, pressures, temperatures, dates, failure reasons, safety rules, regulatory references, locations), each with a `confidence_score`.
- **equipment** — deduplicated by `tag`; `risk_score` is recomputed by the maintenance intelligence engine.
- **maintenance_records / inspection_records** — structured records linked back to both the source `document` and the `equipment` they describe.
- **chat_history** — every AI Chat turn, including retrieved `sources` (JSON) and the confidence score shown in the UI.
- **compliance_records** — recomputed on each `GET /api/compliance` call by the compliance rule engine.
