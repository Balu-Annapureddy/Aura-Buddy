from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.post import Post
from app.models.aura_transaction import AuraTransaction, TransactionType
from app.config import settings


class AuraService:
    """Handles all Aura economy operations with atomic DB transactions."""

    @staticmethod
    def transfer_aura(db: Session, giver: User, post_id: int, amount: int) -> AuraTransaction:
        """Transfer Aura from giver to post author. Atomic."""
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id == giver.id:
            raise HTTPException(status_code=400, detail="Cannot give Aura to your own post")

        if giver.aura_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient Aura balance")

        receiver = db.query(User).filter(User.id == post.user_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Post author not found")

        # Atomic balance update
        giver.aura_balance -= amount
        receiver.aura_balance += amount
        post.aura_score += amount

        transaction = AuraTransaction(
            from_user_id=giver.id,
            to_user_id=receiver.id,
            post_id=post_id,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def hater_tax(db: Session, hater: User, post_id: int, amount: int) -> AuraTransaction:
        """
        Hater tax: post loses X aura, hater loses 2X from balance.
        Enforces balance check on hater for 2X.
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id == hater.id:
            raise HTTPException(status_code=400, detail="Cannot hate on your own post")

        cost_to_hater = amount * 2
        if hater.aura_balance < cost_to_hater:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Hater tax costs 2x ({cost_to_hater} Aura)",
            )

        post_author = db.query(User).filter(User.id == post.user_id).first()
        if not post_author:
            raise HTTPException(status_code=404, detail="Post author not found")

        # Deduct from hater (2x penalty)
        hater.aura_balance -= cost_to_hater
        # Deduct from post author and post score
        post_author.aura_balance -= amount
        post.aura_score -= amount

        # Prevent negative balance on post author — clamp to 0
        if post_author.aura_balance < 0:
            post_author.aura_balance = 0

        transaction = AuraTransaction(
            from_user_id=hater.id,
            to_user_id=post_author.id,
            post_id=post_id,
            amount=-amount,  # Negative to indicate deduction
            transaction_type=TransactionType.HATER_TAX,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def claim_ad_reward(db: Session, user: User) -> AuraTransaction:
        """
        Claim ad reward: +100 Aura.
        Max 2 claims per rolling 12-hour window, validated via DB.
        """
        window_start = datetime.now(timezone.utc) - timedelta(hours=settings.AD_REWARD_WINDOW_HOURS)

        recent_claims = (
            db.query(sql_func.count(AuraTransaction.id))
            .filter(
                AuraTransaction.to_user_id == user.id,
                AuraTransaction.transaction_type == TransactionType.AD_REWARD,
                AuraTransaction.created_at >= window_start,
            )
            .scalar()
        )

        if recent_claims >= settings.AD_REWARD_MAX_CLAIMS:
            raise HTTPException(
                status_code=429,
                detail=f"Ad reward limit reached. Max {settings.AD_REWARD_MAX_CLAIMS} claims per {settings.AD_REWARD_WINDOW_HOURS} hours.",
            )

        user.aura_balance += settings.AD_REWARD_AMOUNT

        transaction = AuraTransaction(
            to_user_id=user.id,
            amount=settings.AD_REWARD_AMOUNT,
            transaction_type=TransactionType.AD_REWARD,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def grant_premium_bonus(db: Session, user: User) -> AuraTransaction:
        """Grant monthly premium Aura bonus."""
        user.aura_balance += settings.PREMIUM_MONTHLY_BONUS

        transaction = AuraTransaction(
            to_user_id=user.id,
            amount=settings.PREMIUM_MONTHLY_BONUS,
            transaction_type=TransactionType.PREMIUM_BONUS,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def grant_mission_reward(db: Session, user: User, auto_commit: bool = True) -> AuraTransaction:
        """
        Grant mission completion Aura reward.
        When called from jury_service (auto_commit=False), the caller handles commit
        to keep the entire vote + reward operation atomic.
        """
        user.aura_balance += settings.MISSION_REWARD_AMOUNT

        transaction = AuraTransaction(
            to_user_id=user.id,
            amount=settings.MISSION_REWARD_AMOUNT,
            transaction_type=TransactionType.MISSION_REWARD,
        )
        db.add(transaction)
        if auto_commit:
            db.commit()
            db.refresh(transaction)
        return transaction
