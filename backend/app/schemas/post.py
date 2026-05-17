import uuid
from datetime import datetime

from pydantic import BaseModel


class PostCreateRequest(BaseModel):
    community_id: uuid.UUID
    content: str
    parent_id: uuid.UUID | None = None


class PostResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    display_name: str          # pseudonym only — author_id is never exposed
    content: str
    parent_id: uuid.UUID | None
    upvotes: int
    is_deleted: bool
    created_at: datetime
    reply_count: int = 0

    model_config = {"from_attributes": True}


class PostFeedResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    page: int
    page_size: int
