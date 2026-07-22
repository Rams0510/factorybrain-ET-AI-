import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, ForeignKey, Enum, Boolean, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PARSED = "parsed"
    EMBEDDED = "embedded"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    role = Column(String(50), default="engineer")
    department = Column(String(120), nullable=True)
    plant = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    documents = relationship("Document", back_populates="owner")
    chats = relationship("ChatMessage", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    owner_id = Column(String(36), ForeignKey("users.id"))
    filename = Column(String(500), nullable=False)
    stored_path = Column(String(1000), nullable=False)
    file_type = Column(String(50))
    doc_category = Column(String(100), nullable=True)  # SOP, Maintenance Report, P&ID, etc
    size_bytes = Column(Integer, default=0)
    status = Column(
        Enum(DocumentStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=DocumentStatus.UPLOADED,
    )
    page_count = Column(Integer, default=0)
    ocr_used = Column(Boolean, default=False)
    extracted_text_preview = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    task_id = Column(String(255), nullable=True)  # Celery task id, for status polling
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    owner = relationship("User", back_populates="documents")
    entities = relationship("ExtractedEntity", back_populates="document")
    maintenance_records = relationship("MaintenanceRecord", back_populates="document")
    inspection_records = relationship("InspectionRecord", back_populates="document")


class ExtractedEntity(Base):
    """Generic entity table: equipment IDs, engineers, dates, pressures, etc."""
    __tablename__ = "extracted_entities"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"))
    entity_type = Column(String(80))  # EQUIPMENT_ID, ENGINEER, PLANT, PRESSURE, TEMPERATURE, DATE, FAILURE_REASON, SAFETY_RULE, REGULATION, LOCATION
    entity_value = Column(String(500))
    confidence_score = Column(Float, default=0.0)
    context_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="entities")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    tag = Column(String(120), unique=True, index=True)  # e.g. P-101
    name = Column(String(255), nullable=True)
    equipment_type = Column(String(100))  # Pump, Valve, Motor, Tank, Pipe
    plant = Column(String(120), nullable=True)
    department = Column(String(120), nullable=True)
    status = Column(String(50), default="operational")
    risk_score = Column(Float, default=0.0)
    install_date = Column(DateTime, nullable=True)
    last_maintenance = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment")
    inspection_records = relationship("InspectionRecord", back_populates="equipment")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    equipment_id = Column(String(36), ForeignKey("equipment.id"), nullable=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    engineer_name = Column(String(255), nullable=True)
    maintenance_date = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    downtime_hours = Column(Float, default=0.0)
    root_cause = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="maintenance_records")
    document = relationship("Document", back_populates="maintenance_records")


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    equipment_id = Column(String(36), ForeignKey("equipment.id"), nullable=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    inspector_name = Column(String(255), nullable=True)
    inspection_date = Column(DateTime, nullable=True)
    findings = Column(Text, nullable=True)
    severity = Column(String(50), nullable=True)  # low, medium, high, critical
    compliant = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="inspection_records")
    document = relationship("Document", back_populates="inspection_records")


class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    session_id = Column(String(36), index=True)
    role = Column(String(20))  # user / assistant
    message = Column(Text)
    sources = Column(JSON, nullable=True)  # list of {document_id, filename, chunk, score}
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    title = Column(String(255))
    message = Column(Text)
    level = Column(String(30), default="info")  # info, warning, critical
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    standard = Column(String(120))  # Factory Act, OISD, PESO, ISO, Environmental
    requirement = Column(String(500))
    status = Column(String(50))  # compliant, missing, expired
    expiry_date = Column(DateTime, nullable=True)
    evidence_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
