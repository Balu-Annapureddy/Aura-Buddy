from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from fastapi import HTTPException

from app.models.user import User
from app.models.post import Post
from app.config import settings


class RateLimiter:
    """Enforces rate limits at DB level — no in-memory caches."""

    @staticmethod
    def check_daily_post_limit(db: Session, user: User) -> None:
        """
        Check if user has exceeded daily post limit.
        Standard: 3 posts per 24h | Premium: 4 posts per 24h.
        """
        limit = (
            settings.DAILY_POST_LIMIT_PREMIUM
            if user.is_premium
            else settings.DAILY_POST_LIMIT_STANDARD
        )

        window_start = datetime.now(timezone.utc) - timedelta(hours=24)

        post_count = (
            db.query(sql_func.count(Post.id))
            .filter(
                Post.user_id == user.id,
                Post.created_at >= window_start,
            )
            .scalar()
        )

        if post_count >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Daily post limit reached ({limit} posts per 24 hours). "
                + ("Upgrade to premium for 4 posts/day." if not user.is_premium else ""),
            )

    @staticmethod
    def get_remaining_posts(db: Session, user: User) -> int:
        """Get number of remaining posts for today."""
        limit = (
            settings.DAILY_POST_LIMIT_PREMIUM
            if user.is_premium
            else settings.DAILY_POST_LIMIT_STANDARD
        )

        window_start = datetime.now(timezone.utc) - timedelta(hours=24)

        post_count = (
            db.query(sql_func.count(Post.id))
            .filter(
                Post.user_id == user.id,
                Post.created_at >= window_start,
            )
            .scalar()
        )

        return max(0, limit - post_count)

    @staticmethod
    def get_remaining_ad_claims(db: Session, user: User) -> int:
        """Get number of remaining ad claims in current window."""
        from app.models.aura_transaction import AuraTransaction, TransactionType

        window_start = datetime.now(timezone.utc) - timedelta(hours=settings.AD_REWARD_WINDOW_HOURS)

        claim_count = (
            db.query(sql_func.count(AuraTransaction.id))
            .filter(
                AuraTransaction.to_user_id == user.id,
                AuraTransaction.transaction_type == TransactionType.AD_REWARD,
                AuraTransaction.created_at >= window_start,
            )
            .scalar()
        )

        return max(0, settings.AD_REWARD_MAX_CLAIMS - claim_count)
