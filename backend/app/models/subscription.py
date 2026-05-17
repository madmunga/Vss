import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    tier: Mapped[str] = mapped_column(Enum("S", "A", "B", name="subscription_tier"), nullable=False)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String, unique=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "CANCELLED", "PAST_DUE", "TRIALING", name="subscription_status"),
        default="TRIALING",
        nullable=False,
    )
    price_usd: Mapped[int] = mapped_column(Integer, nullable=False)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="subscription")
