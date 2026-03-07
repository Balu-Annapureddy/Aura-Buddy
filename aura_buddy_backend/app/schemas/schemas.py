from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- User Schemas ---
class UserCreate(BaseModel):
    firebase_uid: str


class UserSetUsername(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")


class UserResponse(BaseModel):
    id: int
    firebase_uid: str
    username: Optional[str] = None
    aura_balance: int
    is_premium: bool
    premium_expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Post Schemas ---
class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    image_url: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    image_url: Optional[str] = None
    aura_score: int
    created_at: datetime
    author_username: Optional[str] = None

    class Config:
        from_attributes = True


# --- Aura Schemas ---
class AuraTransfer(BaseModel):
    post_id: int
    amount: int = Field(..., gt=0, le=1000)


class HaterTax(BaseModel):
    post_id: int
    amount: int = Field(..., gt=0, le=500)


class AuraTransactionResponse(BaseModel):
    id: int
    from_user_id: Optional[int] = None
    to_user_id: Optional[int] = None
    post_id: Optional[int] = None
    amount: int
    transaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Mission Schemas ---
class MissionCreate(BaseModel):
    mission_type: str
    image_url: Optional[str] = None


class MissionResponse(BaseModel):
    id: int
    user_id: int
    mission_type: str
    image_url: Optional[str] = None
    status: str
    votes_valid: int
    votes_cap: int
    created_at: datetime
    submitter_username: Optional[str] = None

    class Config:
        from_attributes = True


# --- Vote Schemas ---
class VoteCreate(BaseModel):
    mission_id: int
    value: str = Field(..., pattern=r"^(VALID|CAP)$")


class VoteResponse(BaseModel):
    id: int
    user_id: int
    mission_id: int
    value: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Generic ---
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
