import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    create_timed_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.utils.pseudonym import generate_pseudonym


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    real_name: str | None,
    phone: str | None,
    addiction_types: list[str],
) -> User:
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    _validate_password(password)

    # Pre-generate the UUID so the pseudonym can be derived before insert
    user_id = uuid.uuid4()
    pseudonym = generate_pseudonym(str(user_id))

    # Ensure pseudonym is unique (handle the rare hash collision)
    collision = await db.execute(select(User).where(User.display_name == pseudonym))
    if collision.scalar_one_or_none():
        pseudonym = f"{pseudonym}_{str(user_id)[:4]}"

    verification_token = create_timed_token({"sub": str(user_id), "type": "verify"}, expires_in_hours=48)

    user = User(
        id=user_id,
        email=email,
        password_hash=hash_password(password),
        real_name=real_name,
        phone=phone,
        addiction_types=addiction_types,
        display_name=pseudonym,
        verification_token=verification_token,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    if not user.is_active:
        raise ValueError("Account disabled")
    return user


def issue_tokens(user_id: str) -> dict:
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return {"access_token": access, "refresh_token": refresh}


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise ValueError("User not found")

    return issue_tokens(str(user.id))


async def verify_email(db: AsyncSession, token: str) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "verify":
        raise ValueError("Invalid or expired verification link")

    result = await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    user.is_verified = True
    user.verification_token = None
    await db.commit()
    return user


async def initiate_password_reset(db: AsyncSession, email: str) -> str | None:
    """Returns the reset token (caller sends email). Returns None if email not found (silent fail)."""
    from datetime import datetime, timezone, timedelta
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None

    token = create_timed_token({"sub": str(user.id), "type": "reset"}, expires_in_hours=2)  # noqa: F841
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=2)
    await db.commit()
    return token


async def complete_password_reset(db: AsyncSession, token: str, new_password: str) -> None:
    from datetime import datetime, timezone
    payload = decode_token(token)
    if not payload or payload.get("type") != "reset":
        raise ValueError("Invalid or expired reset link")

    result = await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user or user.reset_token != token:
        raise ValueError("Invalid reset token")
    if user.reset_token_expires and user.reset_token_expires < datetime.now(timezone.utc):
        raise ValueError("Reset link has expired")

    _validate_password(new_password)
    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
