import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.database import Base


class MissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MissionType(str, enum.Enum):
    FIT_CHECK = "FIT_CHECK"
    EAT_HEALTHY = "EAT_HEALTHY"
    WORKOUT = "WORKOUT"
    STUDY_SESSION = "STUDY_SESSION"
    RANDOM_ACT = "RANDOM_ACT"


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mission_type = Column(Enum(MissionType, native_enum=False), nullable=False)
    image_url = Column(String(500), nullable=True)
    status = Column(Enum(MissionStatus, native_enum=False), default=MissionStatus.PENDING, nullable=False)
    votes_valid = Column(Integer, default=0, nullable=False)
    votes_cap = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="missions")
    votes = relationship("Vote", back_populates="mission", lazy="dynamic")

    def __repr__(self):
        return f"<Mission {self.id} type={self.mission_type.value} status={self.status.value}>"
