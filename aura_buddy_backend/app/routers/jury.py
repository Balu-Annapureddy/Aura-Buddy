from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.schemas import VoteCreate, VoteResponse
from app.utils.auth import get_current_user
from app.services.jury_service import JuryService

router = APIRouter(prefix="/jury", tags=["Jury"])


@router.post("/vote", response_model=VoteResponse, status_code=201)
def cast_vote(
    data: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cast a VALID or CAP vote on a pending mission."""
    vote = JuryService.cast_vote(db, current_user, data.mission_id, data.value)
    return VoteResponse(
        id=vote.id,
        user_id=vote.user_id,
        mission_id=vote.mission_id,
        value=vote.value.value,
        created_at=vote.created_at,
    )
