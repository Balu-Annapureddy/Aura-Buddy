import enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base


class VoteValue(str, enum.Enum):
    VALID = "VALID"
    CAP = "CAP"


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False, index=True)
    value = Column(Enum(VoteValue, native_enum=False), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Enforce one vote per user per mission at DB level
    __table_args__ = (
        UniqueConstraint("user_id", "mission_id", name="uq_user_mission_vote"),
    )

    # Relationships
    user = relationship("User", back_populates="votes")
    mission = relationship("Mission", back_populates="votes")

    def __repr__(self):
        return f"<Vote user={self.user_id} mission={self.mission_id} value={self.value.value}>"
