from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.services.firebase_auth import verify_id_token, get_or_create_user
from app.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Frontend authenticates with Firebase (Google or Email/Password), then
    sends the resulting Firebase ID token here. We verify it server-side,
    upsert the user in MySQL, and hand back the same token as the session
    token the frontend should attach as a Bearer token on every request.
    """
    decoded = verify_id_token(payload.id_token)
    user = get_or_create_user(db, decoded)
    return LoginResponse(user=UserOut.model_validate(user), session_token=payload.id_token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
