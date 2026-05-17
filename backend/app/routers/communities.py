from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.community import Community, CommunityMembership
from app.models.subscription import Subscription
from app.schemas.community import CommunityListResponse, CommunityResponse
from app.models.user import User

router = APIRouter(prefix="/communities", tags=["communities"])


@router.get("", response_model=CommunityListResponse)
async def list_communities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Community).order_by(Community.name))
    communities = result.scalars().all()
    return CommunityListResponse(communities=communities, total=len(communities))


@router.get("/{slug}", response_model=CommunityResponse)
async def get_community(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Community).where(Community.slug == slug))
    community = result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")
    return community


@router.post("/{slug}/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_community(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.slug == slug))
    community = result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    if community.required_tier:
        sub_result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == current_user.id,
                Subscription.status == "ACTIVE",
                Subscription.tier == community.required_tier,
            )
        )
        if not sub_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Active {community.required_tier}-tier subscription required",
            )

    existing = await db.execute(
        select(CommunityMembership).where(
            CommunityMembership.user_id == current_user.id,
            CommunityMembership.community_id == community.id,
        )
    )
    if existing.scalar_one_or_none():
        return  # already a member — idempotent

    membership = CommunityMembership(user_id=current_user.id, community_id=community.id)
    db.add(membership)
    community.member_count += 1
    await db.commit()


@router.delete("/{slug}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_community(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.slug == slug))
    community = result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    mem_result = await db.execute(
        select(CommunityMembership).where(
            CommunityMembership.user_id == current_user.id,
            CommunityMembership.community_id == community.id,
        )
    )
    membership = mem_result.scalar_one_or_none()
    if membership:
        await db.delete(membership)
        if community.member_count > 0:
            community.member_count -= 1
        await db.commit()
