import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.database import Base


class TransactionType(str, enum.Enum):
    TRANSFER = "TRANSFER"
    HATER_TAX = "HATER_TAX"
    AD_REWARD = "AD_REWARD"
    PREMIUM_BONUS = "PREMIUM_BONUS"
    MISSION_REWARD = "MISSION_REWARD"


class AuraTransaction(Base):
    __tablename__ = "aura_transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, index=True)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(Enum(TransactionType, native_enum=False), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_transactions")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_transactions")
    post = relationship("Post", back_populates="transactions")

    def __repr__(self):
        return f"<AuraTransaction {self.transaction_type.value} amount={self.amount}>"
