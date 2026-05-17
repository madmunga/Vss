import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    real_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    display_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    addiction_types: Mapped[list] = mapped_column(JSON, default=list)
    role: Mapped[str] = mapped_column(
        Enum("USER", "PROFESSIONAL", "ADMIN", name="user_role"),
        default="USER",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_token_hash: Mapped[str | None] = mapped_column(String)
    verification_token: Mapped[str | None] = mapped_column(String)
    reset_token: Mapped[str | None] = mapped_column(String)
    reset_token_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    professional: Mapped["Professional"] = relationship("Professional", back_populates="user", uselist=False)
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="user", uselist=False)
    memberships: Mapped[list["CommunityMembership"]] = relationship("CommunityMembership", back_populates="user")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")
