import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserMeResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    real_name: str | None
    phone: str | None
    display_name: str
    addiction_types: list[str]
    role: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    """Safe public view — real identity fields are intentionally absent."""
    display_name: str

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    real_name: str | None = None
    phone: str | None = None
    addiction_types: list[str] | None = None
