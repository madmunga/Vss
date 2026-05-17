import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ADDICTION_TYPES = ("ALCOHOL", "DRUGS", "GAMBLING", "GAMING", "SEX", "FOOD", "SMOKING", "OTHER")


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    addiction_type: Mapped[str] = mapped_column(
        Enum(*ADDICTION_TYPES, name="addiction_type"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    required_tier: Mapped[str | None] = mapped_column(
        Enum("S", "A", "B", name="community_tier"), nullable=True
    )
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    memberships: Mapped[list["CommunityMembership"]] = relationship(
        "CommunityMembership", back_populates="community"
    )
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="community")
    assignments: Mapped[list["ProfessionalAssignment"]] = relationship(
        "ProfessionalAssignment", back_populates="community"
    )


class CommunityMembership(Base):
    __tablename__ = "community_memberships"
    __table_args__ = (UniqueConstraint("user_id", "community_id", name="uq_membership"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    community_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("communities.id"), nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    community: Mapped["Community"] = relationship("Community", back_populates="memberships")
