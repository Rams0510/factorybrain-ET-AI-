from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import ComplianceReport
from app.services.compliance_engine import run_compliance_check

router = APIRouter(prefix="/api", tags=["compliance"])


@router.get("/compliance", response_model=ComplianceReport)
def compliance_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = run_compliance_check(db)
    return ComplianceReport(**result)
