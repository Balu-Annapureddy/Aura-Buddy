from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserResponse, UserSetUsername
from app.utils.auth import verify_firebase_token, get_current_user, security

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=UserResponse)
def login(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Verify Firebase ID token. Create user if not exists. Return user data.
    """
    token = credentials.credentials
    decoded = verify_firebase_token(token)
    firebase_uid = decoded["uid"]

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        user = User(firebase_uid=firebase_uid)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.post("/username", response_model=UserResponse)
def set_username(
    data: UserSetUsername,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set or update the user's unique username."""
    existing = db.query(User).filter(User.username == data.username).first()
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    current_user.username = data.username
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user
