from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Equipment, MaintenanceRecord
from app.schemas import MaintenanceInsight
from app.services.rag import get_llm
from langchain.schema import HumanMessage, SystemMessage

router = APIRouter(prefix="/api", tags=["maintenance"])


def _compute_risk_score(equipment: Equipment, records: list[MaintenanceRecord]) -> float:
    """
    Heuristic risk score in [0,1]: more failures + more recent failures +
    longer average downtime => higher risk.
    """
    if not records:
        return 0.1

    failure_count = sum(1 for r in records if r.failure_reason)
    avg_downtime = sum(r.downtime_hours or 0 for r in records) / len(records)

    most_recent = max((r.maintenance_date for r in records if r.maintenance_date), default=None)
    recency_factor = 0.0
    if most_recent:
        days_since = (datetime.utcnow() - most_recent).days
        recency_factor = max(0.0, 1 - (days_since / 180))  # decays over ~6 months

    score = min(1.0, (failure_count * 0.15) + (avg_downtime / 100) + (recency_factor * 0.3))
    return round(score, 2)


@router.get("/maintenance", response_model=list[MaintenanceInsight])
def maintenance_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    equipment_list = db.query(Equipment).all()
    insights = []

    for eq in equipment_list:
        records = (
            db.query(MaintenanceRecord)
            .filter(MaintenanceRecord.equipment_id == eq.id)
            .order_by(MaintenanceRecord.maintenance_date.desc())
            .all()
        )
        risk_score = _compute_risk_score(eq, records)
        eq.risk_score = risk_score

        if not records:
            insights.append(MaintenanceInsight(
                equipment_tag=eq.tag,
                root_cause_analysis="No maintenance history recorded yet.",
                recommendations=["Schedule a baseline inspection to establish maintenance history."],
                risk_score=risk_score,
                predicted_next_failure_window_days=None,
            ))
            continue

        failure_reasons = [r.failure_reason for r in records if r.failure_reason]
        rca_text = "; ".join(failure_reasons[:5]) if failure_reasons else "No recorded failures."

        recommendations = []
        if risk_score >= 0.7:
            recommendations.append(f"High risk: schedule immediate inspection of {eq.tag}.")
        if failure_reasons:
            recommendations.append("Review root causes and consider preventive part replacement.")
        if not recommendations:
            recommendations.append("Continue routine preventive maintenance schedule.")

        predicted_window = int(30 + (1 - risk_score) * 150) if risk_score > 0 else None

        insights.append(MaintenanceInsight(
            equipment_tag=eq.tag,
            root_cause_analysis=rca_text,
            recommendations=recommendations,
            risk_score=risk_score,
            predicted_next_failure_window_days=predicted_window,
        ))

    db.commit()
    return insights


@router.get("/maintenance/{tag}/ai-analysis")
def ai_root_cause_analysis(tag: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Uses Gemini to generate a narrative root-cause-analysis from stored maintenance text."""
    equipment = db.query(Equipment).filter(Equipment.tag == tag).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    records = db.query(MaintenanceRecord).filter(MaintenanceRecord.equipment_id == equipment.id).all()
    history_text = "\n".join(
        f"- {r.maintenance_date}: failure='{r.failure_reason}', action='{r.action_taken}', root_cause='{r.root_cause}'"
        for r in records
    ) or "No maintenance records available."

    llm = get_llm()
    messages = [
        SystemMessage(content="You are an industrial reliability engineer. Analyze the maintenance history and "
                               "produce: 1) Root Cause Analysis 2) Concrete recommendations 3) A qualitative risk assessment."),
        HumanMessage(content=f"Equipment: {tag}\nMaintenance history:\n{history_text}"),
    ]
    response = llm.invoke(messages)
    return {"equipment_tag": tag, "analysis": response.content}
