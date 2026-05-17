import uuid
from datetime import datetime

from pydantic import BaseModel


class CommunityResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    addiction_type: str
    description: str | None
    required_tier: str | None
    member_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CommunityListResponse(BaseModel):
    communities: list[CommunityResponse]
    total: int
