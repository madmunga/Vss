import uuid
from datetime import datetime

from pydantic import BaseModel


class TierInfo(BaseModel):
    tier: str
    price_usd: int
    description: str
    features: list[str]


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    tier: str
    status: str
    price_usd: int
    current_period_start: datetime | None
    current_period_end: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    tier: str


class CheckoutResponse(BaseModel):
    checkout_url: str
