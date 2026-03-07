from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.mission import Mission, MissionStatus
from app.models.vote import Vote, VoteValue
from app.models.user import User
from app.services.aura_service import AuraService
from app.config import settings


class JuryService:
    """Community jury voting system — no AI moderation."""

    @staticmethod
    def cast_vote(db: Session, user: User, mission_id: int, vote_value: str) -> Vote:
        """
        Cast a vote on a mission. Each user can vote once per mission.
        When threshold is reached, mission is approved/rejected.
        """
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        if mission.status != MissionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Mission is no longer pending")

        if mission.user_id == user.id:
            raise HTTPException(status_code=400, detail="Cannot vote on your own mission")

        # Check if user already voted (also enforced by DB unique constraint)
        existing_vote = (
            db.query(Vote)
            .filter(Vote.user_id == user.id, Vote.mission_id == mission_id)
            .first()
        )
        if existing_vote:
            raise HTTPException(status_code=400, detail="You have already voted on this mission")

        # Create the vote
        vote_enum = VoteValue.VALID if vote_value == "VALID" else VoteValue.CAP
        vote = Vote(
            user_id=user.id,
            mission_id=mission_id,
            value=vote_enum,
        )
        db.add(vote)

        # Update mission vote counters
        if vote_enum == VoteValue.VALID:
            mission.votes_valid += 1
        else:
            mission.votes_cap += 1

        # Check thresholds
        if mission.votes_valid >= settings.MISSION_APPROVAL_THRESHOLD:
            mission.status = MissionStatus.APPROVED
            # Award mission Aura to the submitter
            mission_owner = db.query(User).filter(User.id == mission.user_id).first()
            if mission_owner:
                AuraService.grant_mission_reward(db, mission_owner, auto_commit=False)
        elif mission.votes_cap >= settings.MISSION_REJECTION_THRESHOLD:
            mission.status = MissionStatus.REJECTED

        db.commit()
        db.refresh(vote)
        return vote

    @staticmethod
    def get_pending_missions(db: Session, limit: int = 20, offset: int = 0):
        """Get global list of pending missions for the jury queue."""
        return (
            db.query(Mission)
            .filter(Mission.status == MissionStatus.PENDING)
            .order_by(Mission.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
