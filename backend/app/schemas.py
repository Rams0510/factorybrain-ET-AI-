from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime


# ---------- Auth ----------
class LoginRequest(BaseModel):
    id_token: str  # Firebase ID token from frontend


class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    photo_url: Optional[str] = None
    role: str
    department: Optional[str] = None
    plant: Optional[str] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    user: UserOut
    session_token: str


# ---------- Documents ----------
class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: Optional[str]
    doc_category: Optional[str]
    size_bytes: int
    status: str
    page_count: int
    ocr_used: bool
    chunk_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    extracted_text_preview: Optional[str] = None
    task_id: Optional[str] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    uploaded: List[DocumentOut]


# ---------- Equipment ----------
class EquipmentOut(BaseModel):
    id: str
    tag: str
    name: Optional[str]
    equipment_type: str
    plant: Optional[str]
    department: Optional[str]
    status: str
    risk_score: float
    last_maintenance: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class SourceRef(BaseModel):
    document_id: str
    filename: str
    chunk_text: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    confidence_score: float
    sources: List[SourceRef]


# ---------- Analytics ----------
class AnalyticsOverview(BaseModel):
    total_documents: int
    total_equipment: int
    recent_uploads: int
    compliance_score: float
    open_maintenance_alerts: int
    documents_by_category: Dict[str, int]
    equipment_by_type: Dict[str, int]
    maintenance_trend: List[Dict[str, Any]]
    compliance_trend: List[Dict[str, Any]]
    failure_trend: List[Dict[str, Any]]


# ---------- Graph ----------
class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# ---------- Maintenance ----------
class MaintenanceInsight(BaseModel):
    equipment_tag: str
    root_cause_analysis: str
    recommendations: List[str]
    risk_score: float
    predicted_next_failure_window_days: Optional[int] = None


# ---------- Compliance ----------
class ComplianceItem(BaseModel):
    standard: str
    requirement: str
    status: str
    expiry_date: Optional[datetime] = None
    document_id: Optional[str] = None


class ComplianceReport(BaseModel):
    overall_score: float
    items: List[ComplianceItem]
    missing_reports: List[str]
    expired_certificates: List[str]
