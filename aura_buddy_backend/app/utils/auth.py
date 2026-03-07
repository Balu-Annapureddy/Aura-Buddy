"""
Firebase Authentication utilities.
Verifies Firebase ID tokens and provides a FastAPI dependency for auth.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

security = HTTPBearer()

# Firebase Admin SDK initialization
_firebase_app = None


def _init_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
        from app.config import settings

        if settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            # Use default credentials (for Cloud Run / Firebase hosting)
            _firebase_app = firebase_admin.initialize_app()
    except Exception:
        # Allow running without Firebase for development
        _firebase_app = "MOCK"


def verify_firebase_token(token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims."""
    _init_firebase()

    if _firebase_app == "MOCK":
        # Development mode: treat token as firebase_uid
        return {"uid": token, "email": f"{token}@dev.local"}

    try:
        from firebase_admin import auth
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {str(e)}",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: verify token and return the current User object."""
    token = credentials.credentials
    decoded = verify_firebase_token(token)
    firebase_uid = decoded["uid"]

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete registration first.",
        )
    return user
