from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.subscription import SubscriptionResponse
from app.schemas.user import UserMeResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserMeResponse)
async def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.real_name is not None:
        current_user.real_name = body.real_name
    if body.phone is not None:
        current_user.phone = body.phone
    if body.addiction_types is not None:
        current_user.addiction_types = body.addiction_types
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/subscription", response_model=SubscriptionResponse | None)
async def get_my_subscription(current_user: User = Depends(get_current_user)):
    return current_user.subscription
