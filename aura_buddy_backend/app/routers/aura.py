from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.schemas import AuraTransfer, HaterTax, AuraTransactionResponse
from app.utils.auth import get_current_user
from app.services.aura_service import AuraService
from app.services.rate_limiter import RateLimiter

router = APIRouter(prefix="/aura", tags=["Aura Economy"])


@router.post("/transfer", response_model=AuraTransactionResponse)
def transfer_aura(
    data: AuraTransfer,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Award Aura to another user's post. Deducts from giver, adds to receiver."""
    txn = AuraService.transfer_aura(db, current_user, data.post_id, data.amount)
    return AuraTransactionResponse(
        id=txn.id,
        from_user_id=txn.from_user_id,
        to_user_id=txn.to_user_id,
        post_id=txn.post_id,
        amount=txn.amount,
        transaction_type=txn.transaction_type.value,
        created_at=txn.created_at,
    )


@router.post("/hater-tax", response_model=AuraTransactionResponse)
def hater_tax(
    data: HaterTax,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply hater tax: post loses X, hater loses 2X from balance."""
    txn = AuraService.hater_tax(db, current_user, data.post_id, data.amount)
    return AuraTransactionResponse(
        id=txn.id,
        from_user_id=txn.from_user_id,
        to_user_id=txn.to_user_id,
        post_id=txn.post_id,
        amount=txn.amount,
        transaction_type=txn.transaction_type.value,
        created_at=txn.created_at,
    )


@router.post("/claim-ad-reward", response_model=AuraTransactionResponse)
def claim_ad_reward(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Claim ad reward (+100 Aura). Max 2 per 12-hour window."""
    txn = AuraService.claim_ad_reward(db, current_user)
    return AuraTransactionResponse(
        id=txn.id,
        from_user_id=txn.from_user_id,
        to_user_id=txn.to_user_id,
        post_id=txn.post_id,
        amount=txn.amount,
        transaction_type=txn.transaction_type.value,
        created_at=txn.created_at,
    )


@router.get("/remaining-ad-claims")
def get_remaining_ad_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get remaining ad reward claims in the current 12-hour window."""
    remaining = RateLimiter.get_remaining_ad_claims(db, current_user)
    return {"remaining_ad_claims": remaining}
