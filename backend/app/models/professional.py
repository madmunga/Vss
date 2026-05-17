import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    specialty: Mapped[str] = mapped_column(
        Enum("PSYCHIATRIST", "PSYCHOLOGIST", "COUNSELOR", "THERAPIST", "ADVISOR", name="professional_specialty"),
        nullable=False,
    )
    tier: Mapped[str] = mapped_column(Enum("S", "A", "B", name="professional_tier"), nullable=False)
    vetting_status: Mapped[str] = mapped_column(
        Enum("PENDING", "APPROVED", "REJECTED", name="vetting_status"),
        default="PENDING",
        nullable=False,
    )
    vetting_facility: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    years_experience: Mapped[int | None] = mapped_column(Integer)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="professional")
    assignments: Mapped[list["ProfessionalAssignment"]] = relationship(
        "ProfessionalAssignment", back_populates="professional"
    )


class ProfessionalAssignment(Base):
    __tablename__ = "professional_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("professionals.id"), nullable=False
    )
    community_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("communities.id"), nullable=False
    )
    tier: Mapped[str] = mapped_column(Enum("S", "A", "B", name="assignment_tier"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    professional: Mapped["Professional"] = relationship("Professional", back_populates="assignments")
    community: Mapped["Community"] = relationship("Community", back_populates="assignments")
