"""
Checks uploaded documents against required industrial standards
(Factory Act, OISD, PESO, ISO, Environmental Standards) using the
REGULATORY_REFERENCE entities already extracted from documents, plus a
required-document checklist per standard.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Document, ExtractedEntity, ComplianceRecord

REQUIRED_DOCUMENT_CATEGORIES = {
    "Factory Act": ["Safety Manual", "Inspection Report"],
    "OISD": ["Audit Report", "Engineering Drawing (P&ID)"],
    "PESO": ["Safety Manual"],
    "ISO": ["SOP", "Audit Report"],
    "Environmental Standards": ["Audit Report"],
}


def run_compliance_check(db: Session) -> dict:
    """
    Recomputes ComplianceRecord rows based on current documents and
    regulatory-reference entities, then returns an aggregate report.
    """
    db.query(ComplianceRecord).delete()

    categories_present = {
        row[0] for row in db.query(Document.doc_category).distinct().all() if row[0]
    }

    missing_reports = []
    items = []

    for standard, required_categories in REQUIRED_DOCUMENT_CATEGORIES.items():
        for category in required_categories:
            if category in categories_present:
                doc = db.query(Document).filter(Document.doc_category == category).first()
                db.add(ComplianceRecord(
                    document_id=doc.id if doc else None,
                    standard=standard,
                    requirement=f"{category} on file",
                    status="compliant",
                ))
                items.append({
                    "standard": standard,
                    "requirement": f"{category} on file",
                    "status": "compliant",
                    "document_id": doc.id if doc else None,
                })
            else:
                db.add(ComplianceRecord(
                    document_id=None,
                    standard=standard,
                    requirement=f"{category} on file",
                    status="missing",
                ))
                missing_reports.append(f"{standard}: {category}")
                items.append({"standard": standard, "requirement": f"{category} on file", "status": "missing"})

    # Expired certificates: regulatory references mentioned in documents
    # older than 365 days are flagged as potentially expired (heuristic —
    # true certificate expiry dates require structured certificate data).
    expired_certificates = []
    cutoff = datetime.utcnow() - timedelta(days=365)
    old_reg_docs = (
        db.query(Document)
        .join(ExtractedEntity, ExtractedEntity.document_id == Document.id)
        .filter(ExtractedEntity.entity_type == "REGULATORY_REFERENCE", Document.uploaded_at < cutoff)
        .distinct()
        .all()
    )
    for doc in old_reg_docs:
        expired_certificates.append(doc.filename)
        db.add(ComplianceRecord(
            document_id=doc.id,
            standard="General",
            requirement="Regulatory reference re-certification",
            status="expired",
            expiry_date=doc.uploaded_at + timedelta(days=365),
        ))

    db.commit()

    total = len(items) + len(expired_certificates)
    compliant_count = sum(1 for i in items if i["status"] == "compliant")
    score = round((compliant_count / total) * 100, 1) if total else 100.0

    return {
        "overall_score": score,
        "items": items,
        "missing_reports": missing_reports,
        "expired_certificates": expired_certificates,
    }