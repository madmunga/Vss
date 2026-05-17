import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageSendRequest(BaseModel):
    recipient_id: uuid.UUID
    content: str


class MessageResponse(BaseModel):
    id: uuid.UUID
    sender_display_name: str
    recipient_display_name: str
    content: str
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    other_user_id: uuid.UUID
    other_display_name: str
    last_message: str
    last_message_at: datetime
    unread_count: int
