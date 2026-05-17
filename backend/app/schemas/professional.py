import uuid
from datetime import datetime

from pydantic import BaseModel


class ProfessionalEnrollRequest(BaseModel):
    license_number: str
    specialty: str
    tier: str
    vetting_facility: str
    bio: str | None = None
    years_experience: int | None = None
    languages: list[str] = ["en"]


class ProfessionalResponse(BaseModel):
    id: uuid.UUID
    display_name: str          # from the linked user — real name never exposed
    specialty: str
    tier: str
    vetting_status: str
    bio: str | None
    years_experience: int | None
    languages: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class VetRequest(BaseModel):
    status: str               # "APPROVED" or "REJECTED"
    vetting_facility: str | None = None
