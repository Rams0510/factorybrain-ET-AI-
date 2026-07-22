from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Document, Equipment, MaintenanceRecord, ComplianceRecord
from app.schemas import AnalyticsOverview

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsOverview)
def analytics_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_equipment = db.query(func.count(Equipment.id)).scalar() or 0

    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_uploads = db.query(func.count(Document.id)).filter(Document.uploaded_at >= week_ago).scalar() or 0

    docs_by_cat_rows = (
        db.query(Document.doc_category, func.count(Document.id))
        .group_by(Document.doc_category)
        .all()
    )
    documents_by_category = {cat or "Uncategorized": count for cat, count in docs_by_cat_rows}

    equip_by_type_rows = (
        db.query(Equipment.equipment_type, func.count(Equipment.id))
        .group_by(Equipment.equipment_type)
        .all()
    )
    equipment_by_type = {t or "Unknown": count for t, count in equip_by_type_rows}

    open_alerts = db.query(func.count(Equipment.id)).filter(Equipment.risk_score >= 0.7).scalar() or 0

    compliant = db.query(func.count(ComplianceRecord.id)).filter(ComplianceRecord.status == "compliant").scalar() or 0
    total_compliance_items = db.query(func.count(ComplianceRecord.id)).scalar() or 0
    compliance_score = round((compliant / total_compliance_items) * 100, 1) if total_compliance_items else 100.0

    # Trends: last 6 months, grouped by month
    maintenance_trend = []
    compliance_trend = []
    failure_trend = []
    for i in range(5, -1, -1):
        month_start = (datetime.utcnow().replace(day=1) - timedelta(days=30 * i))
        label = month_start.strftime("%b")

        maint_count = (
            db.query(func.count(MaintenanceRecord.id))
            .filter(func.month(MaintenanceRecord.maintenance_date) == month_start.month)
            .scalar()
            or 0
        )
        maintenance_trend.append({"month": label, "count": maint_count})

        failures = (
            db.query(func.count(MaintenanceRecord.id))
            .filter(
                func.month(MaintenanceRecord.maintenance_date) == month_start.month,
                MaintenanceRecord.failure_reason.isnot(None),
            )
            .scalar()
            or 0
        )
        failure_trend.append({"month": label, "count": failures})

        compliance_trend.append({"month": label, "score": compliance_score})

    return AnalyticsOverview(
        total_documents=total_documents,
        total_equipment=total_equipment,
        recent_uploads=recent_uploads,
        compliance_score=compliance_score,
        open_maintenance_alerts=open_alerts,
        documents_by_category=documents_by_category,
        equipment_by_type=equipment_by_type,
        maintenance_trend=maintenance_trend,
        compliance_trend=compliance_trend,
        failure_trend=failure_trend,
    )
