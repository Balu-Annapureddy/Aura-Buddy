from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.mission import Mission, MissionType, MissionStatus
from app.schemas.schemas import MissionCreate, MissionResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.post("/", response_model=MissionResponse, status_code=201)
def create_mission(
    data: MissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new mission for community validation."""
    if not current_user.username:
        raise HTTPException(status_code=400, detail="Set a username before submitting missions")

    # Validate mission type
    try:
        mission_type = MissionType(data.mission_type)
    except ValueError:
        valid_types = [t.value for t in MissionType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mission type. Must be one of: {valid_types}",
        )

    mission = Mission(
        user_id=current_user.id,
        mission_type=mission_type,
        image_url=data.image_url,
        status=MissionStatus.PENDING,
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)

    return MissionResponse(
        id=mission.id,
        user_id=mission.user_id,
        mission_type=mission.mission_type.value,
        image_url=mission.image_url,
        status=mission.status.value,
        votes_valid=mission.votes_valid,
        votes_cap=mission.votes_cap,
        created_at=mission.created_at,
        submitter_username=current_user.username,
    )


@router.get("/pending", response_model=List[MissionResponse])
def get_pending_missions(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get global list of pending missions for the jury queue."""
    missions = (
        db.query(Mission)
        .filter(Mission.status == MissionStatus.PENDING)
        .order_by(Mission.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        MissionResponse(
            id=m.id,
            user_id=m.user_id,
            mission_type=m.mission_type.value,
            image_url=m.image_url,
            status=m.status.value,
            votes_valid=m.votes_valid,
            votes_cap=m.votes_cap,
            created_at=m.created_at,
            submitter_username=m.user.username if m.user else None,
        )
        for m in missions
    ]


@router.get("/my", response_model=List[MissionResponse])
def get_my_missions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's submitted missions."""
    missions = (
        db.query(Mission)
        .filter(Mission.user_id == current_user.id)
        .order_by(Mission.created_at.desc())
        .all()
    )

    return [
        MissionResponse(
            id=m.id,
            user_id=m.user_id,
            mission_type=m.mission_type.value,
            image_url=m.image_url,
            status=m.status.value,
            votes_valid=m.votes_valid,
            votes_cap=m.votes_cap,
            created_at=m.created_at,
            submitter_username=current_user.username,
        )
        for m in missions
    ]
