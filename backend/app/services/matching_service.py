import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import Community
from app.models.professional import Professional, ProfessionalAssignment


async def assign_professional_to_community(
    professional_id: uuid.UUID,
    community_id: uuid.UUID,
    tier: str,
    db: AsyncSession,
) -> ProfessionalAssignment:
    result = await db.execute(
        select(ProfessionalAssignment).where(
            ProfessionalAssignment.professional_id == professional_id,
            ProfessionalAssignment.community_id == community_id,
            ProfessionalAssignment.is_active == True,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    assignment = ProfessionalAssignment(
        professional_id=professional_id,
        community_id=community_id,
        tier=tier,
        is_active=True,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def get_communities_for_professional(
    professional_id: uuid.UUID,
    db: AsyncSession,
) -> list[Community]:
    result = await db.execute(
        select(Community)
        .join(ProfessionalAssignment, ProfessionalAssignment.community_id == Community.id)
        .where(
            ProfessionalAssignment.professional_id == professional_id,
            ProfessionalAssignment.is_active == True,
        )
    )
    return list(result.scalars().all())


async def get_professionals_for_community(
    community_id: uuid.UUID,
    db: AsyncSession,
) -> list[Professional]:
    result = await db.execute(
        select(Professional)
        .join(ProfessionalAssignment, ProfessionalAssignment.professional_id == Professional.id)
        .where(
            ProfessionalAssignment.community_id == community_id,
            ProfessionalAssignment.is_active == True,
            Professional.vetting_status == "APPROVED",
        )
    )
    return list(result.scalars().all())
