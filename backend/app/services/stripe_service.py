from datetime import datetime, timezone

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.subscription import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

TIER_PRICES = {"S": 50, "A": 30, "B": 10}


async def create_checkout_session(user_id: str, user_email: str, tier: str, db: AsyncSession) -> str:
    if tier not in TIER_PRICES:
        raise ValueError(f"Invalid tier: {tier}")

    price_id = settings.stripe_price_map.get(tier)
    if not price_id:
        raise ValueError("Stripe price not configured for this tier")

    session = stripe.checkout.Session.create(
        customer_email=user_email,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.FRONTEND_URL}/subscribe/success?tier={tier}",
        cancel_url=f"{settings.FRONTEND_URL}/subscribe",
        metadata={"user_id": user_id, "tier": tier},
    )
    return session.url


async def handle_webhook(payload: bytes, sig_header: str, db: AsyncSession) -> None:
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError:
        raise ValueError("Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _on_checkout_completed(data, db)
    elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
        await _on_subscription_updated(data, db)
    elif event_type == "customer.subscription.deleted":
        await _on_subscription_cancelled(data, db)
    elif event_type == "invoice.payment_failed":
        await _on_payment_failed(data, db)


async def _on_checkout_completed(session: dict, db: AsyncSession) -> None:
    user_id = session["metadata"]["user_id"]
    tier = session["metadata"]["tier"]
    stripe_sub_id = session.get("subscription")
    customer_id = session.get("customer")

    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalar_one_or_none()

    if sub:
        sub.tier = tier
        sub.stripe_subscription_id = stripe_sub_id
        sub.stripe_customer_id = customer_id
        sub.status = "ACTIVE"
        sub.price_usd = TIER_PRICES[tier]
    else:
        sub = Subscription(
            user_id=user_id,
            tier=tier,
            stripe_subscription_id=stripe_sub_id,
            stripe_customer_id=customer_id,
            status="ACTIVE",
            price_usd=TIER_PRICES[tier],
        )
        db.add(sub)
    await db.commit()


async def _on_subscription_updated(stripe_sub: dict, db: AsyncSession) -> None:
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub["id"])
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return

    status_map = {"active": "ACTIVE", "past_due": "PAST_DUE", "trialing": "TRIALING", "canceled": "CANCELLED"}
    sub.status = status_map.get(stripe_sub["status"], sub.status)
    sub.current_period_start = datetime.fromtimestamp(stripe_sub["current_period_start"], tz=timezone.utc)
    sub.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"], tz=timezone.utc)
    await db.commit()


async def _on_subscription_cancelled(stripe_sub: dict, db: AsyncSession) -> None:
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub["id"])
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = "CANCELLED"
        await db.commit()


async def _on_payment_failed(invoice: dict, db: AsyncSession) -> None:
    sub_id = invoice.get("subscription")
    if not sub_id:
        return
    result = await db.execute(select(Subscription).where(Subscription.stripe_subscription_id == sub_id))
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = "PAST_DUE"
        await db.commit()
