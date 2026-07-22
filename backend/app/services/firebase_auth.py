"""
Verifies Firebase ID tokens issued by the frontend (Google Login / Email
Login via Firebase Authentication) and syncs the user into MySQL.
"""
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.config import get_settings
from app.models import User

settings = get_settings()
_initialized = False


def init_firebase():
    global _initialized
    if not _initialized:
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
            print(f"[firebase] Initialized successfully for project '{settings.FIREBASE_PROJECT_ID}' "
                  f"using credentials at {settings.FIREBASE_CREDENTIALS_PATH}")
        except Exception as exc:
            # Allows the app to boot even before the service-account file is
            # mounted, but logs loudly so misconfiguration is diagnosable
            # from `docker-compose logs backend` instead of failing silently.
            print(f"[firebase] INIT FAILED: {exc}")
            print(f"[firebase] Check that FIREBASE_CREDENTIALS_PATH "
                  f"({settings.FIREBASE_CREDENTIALS_PATH}) exists and is readable, "
                  f"and that FIREBASE_PROJECT_ID ({settings.FIREBASE_PROJECT_ID}) "
                  f"matches your Firebase project's real Project ID.")
        _initialized = True


def verify_id_token(id_token: str) -> dict:
    init_firebase()
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {exc}",
        )


def get_or_create_user(db: Session, decoded_token: dict) -> User:
    firebase_uid = decoded_token["uid"]
    email = decoded_token.get("email", "")
    name = decoded_token.get("name")
    picture = decoded_token.get("picture")

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user is None:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            photo_url=picture,
        )
        db.add(user)
    else:
        user.last_login = datetime.utcnow()
        user.name = name or user.name
        user.photo_url = picture or user.photo_url

    db.commit()
    db.refresh(user)
    return user