from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.utils.pseudonym import generate_pseudonym


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

    user = User(
        email=email,
        password_hash=hash_password(password),
        real_name=real_name,
        phone=phone,
        addiction_types=addiction_types,
        display_name="__temp__",  # placeholder replaced below after flush
    )
    db.add(user)
    await db.flush()  # populate user.id without committing

    user.display_name = generate_pseudonym(str(user.id))
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

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise ValueError("User not found")

    return issue_tokens(str(user.id))
