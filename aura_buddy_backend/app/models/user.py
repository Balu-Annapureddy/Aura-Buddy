import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    username = Column(String(30), unique=True, nullable=True, index=True)
    aura_balance = Column(Integer, default=0, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    premium_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    posts = relationship("Post", back_populates="author", lazy="dynamic")
    missions = relationship("Mission", back_populates="user", lazy="dynamic")
    votes = relationship("Vote", back_populates="user", lazy="dynamic")
    sent_transactions = relationship(
        "AuraTransaction",
        foreign_keys="AuraTransaction.from_user_id",
        back_populates="from_user",
        lazy="dynamic",
    )
    received_transactions = relationship(
        "AuraTransaction",
        foreign_keys="AuraTransaction.to_user_id",
        back_populates="to_user",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<User {self.username} | Aura: {self.aura_balance}>"
