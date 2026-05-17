from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionResponse,
    TierInfo,
)
from app.services import stripe_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

TIER_DETAILS = [
    TierInfo(
        tier="S",
        price_usd=50,
        description="Premium: Access to the most experienced psychiatrists and senior therapists.",
        features=[
            "Assigned S-tier psychiatrist",
            "Priority group access",
            "All community tiers",
            "Monthly group session",
        ],
    ),
    TierInfo(
        tier="A",
        price_usd=30,
        description="Advanced: Experienced psychologists and senior counselors.",
        features=[
            "Assigned A-tier psychologist",
            "A & B community access",
            "Bi-monthly group session",
        ],
    ),
    TierInfo(
        tier="B",
        price_usd=10,
        description="Essential: Capable licensed counselors and advisors.",
        features=[
            "Assigned B-tier counselor",
            "B community access",
            "Community peer support",
        ],
    ),
]


@router.get("/tiers", response_model=list[TierInfo])
async def get_tiers():
    return TIER_DETAILS


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.tier not in ("S", "A", "B"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid tier")
    try:
        url = await stripe_service.create_checkout_session(
            user_id=str(current_user.id),
            user_email=current_user.email,
            tier=body.tier,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return CheckoutResponse(checkout_url=url)


@router.post("/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        await stripe_service.handle_webhook(payload, sig_header, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "ACTIVE",
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if sub.stripe_subscription_id:
        stripe.Subscription.cancel(sub.stripe_subscription_id)
    sub.status = "CANCELLED"
    await db.commit()
