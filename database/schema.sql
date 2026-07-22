-- FactoryBrain AI — MySQL Schema
-- This file is auto-mounted into the MySQL container's
-- /docker-entrypoint-initdb.d/ and runs once on first container start.
-- The FastAPI backend also calls SQLAlchemy's create_all() on startup,
-- which is idempotent — so this file and the ORM models in
-- backend/app/models.py always describe the same schema.

CREATE DATABASE IF NOT EXISTS factorybrain CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE factorybrain;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    photo_url VARCHAR(500),
    role VARCHAR(50) DEFAULT 'engineer',
    department VARCHAR(120),
    plant VARCHAR(120),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY,
    owner_id VARCHAR(36),
    filename VARCHAR(500) NOT NULL,
    stored_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50),
    doc_category VARCHAR(100),
    size_bytes INT DEFAULT 0,
    status ENUM('uploaded','processing','parsed','embedded','failed') DEFAULT 'uploaded',
    page_count INT DEFAULT 0,
    ocr_used BOOLEAN DEFAULT FALSE,
    extracted_text_preview TEXT,
    chunk_count INT DEFAULT 0,
    task_id VARCHAR(255) NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME NULL,
    error_message TEXT,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS extracted_entities (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36),
    entity_type VARCHAR(80),
    entity_value VARCHAR(500),
    confidence_score FLOAT DEFAULT 0,
    context_snippet TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS equipment (
    id VARCHAR(36) PRIMARY KEY,
    tag VARCHAR(120) UNIQUE,
    name VARCHAR(255),
    equipment_type VARCHAR(100),
    plant VARCHAR(120),
    department VARCHAR(120),
    status VARCHAR(50) DEFAULT 'operational',
    risk_score FLOAT DEFAULT 0,
    install_date DATETIME NULL,
    last_maintenance DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    id VARCHAR(36) PRIMARY KEY,
    equipment_id VARCHAR(36),
    document_id VARCHAR(36),
    engineer_name VARCHAR(255),
    maintenance_date DATETIME NULL,
    failure_reason TEXT,
    action_taken TEXT,
    downtime_hours FLOAT DEFAULT 0,
    root_cause TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE SET NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inspection_records (
    id VARCHAR(36) PRIMARY KEY,
    equipment_id VARCHAR(36),
    document_id VARCHAR(36),
    inspector_name VARCHAR(255),
    inspection_date DATETIME NULL,
    findings TEXT,
    severity VARCHAR(50),
    compliant BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE SET NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS chat_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    role VARCHAR(20),
    message TEXT,
    sources JSON,
    confidence_score FLOAT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    title VARCHAR(255),
    message TEXT,
    level VARCHAR(30) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS compliance_records (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36),
    standard VARCHAR(120),
    requirement VARCHAR(500),
    status VARCHAR(50),
    expiry_date DATETIME NULL,
    evidence_snippet TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_entities_document ON extracted_entities(document_id);
CREATE INDEX idx_maintenance_equipment ON maintenance_records(equipment_id);
CREATE INDEX idx_inspection_equipment ON inspection_records(equipment_id);
CREATE INDEX idx_chat_session ON chat_history(session_id);
