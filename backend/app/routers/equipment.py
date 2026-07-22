from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models import Equipment, User
from app.schemas import EquipmentOut

router = APIRouter(prefix="/api", tags=["equipment"])


@router.get("/equipment", response_model=List[EquipmentOut])
def list_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    equipment_type: str | None = None,
    plant: str | None = None,
):
    query = db.query(Equipment)
    if equipment_type:
        query = query.filter(Equipment.equipment_type == equipment_type)
    if plant:
        query = query.filter(Equipment.plant == plant)
    return query.order_by(Equipment.risk_score.desc()).all()


@router.get("/equipment/{tag}", response_model=EquipmentOut)
def get_equipment(tag: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Equipment).filter(Equipment.tag == tag).first()
