"""Admin-only router: professional vetting, community management, assignments."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.community import Community
from app.models.professional import Professional, ProfessionalAssignment
from app.models.user import User
from app.schemas.community import CommunityResponse
from app.schemas.professional import ProfessionalResponse, VetRequest
from app.services.matching_service import assign_professional_to_community
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


class CommunityCreateRequest(BaseModel):
    name: str
    slug: str
    addiction_type: str
    description: str | None = None
    required_tier: str | None = None


class AssignRequest(BaseModel):
    professional_id: uuid.UUID
    community_id: uuid.UUID


@router.get("/professionals/pending", response_model=list[ProfessionalResponse])
async def list_pending_professionals(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Professional).where(Professional.vetting_status == "PENDING").order_by(Professional.created_at)
    )
    professionals = result.scalars().all()
    responses = []
    for p in professionals:
        await db.refresh(p, ["user"])
        responses.append(
            ProfessionalResponse(
                id=p.id,
                display_name=p.user.display_name,
                specialty=p.specialty,
                tier=p.tier,
                vetting_status=p.vetting_status,
                bio=p.bio,
                years_experience=p.years_experience,
                languages=p.languages,
                created_at=p.created_at,
            )
        )
    return responses


@router.put("/professionals/{professional_id}/vet", response_model=ProfessionalResponse)
async def vet_professional(
    professional_id: uuid.UUID,
    body: VetRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if body.status not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status must be APPROVED or REJECTED")

    result = await db.execute(select(Professional).where(Professional.id == professional_id))
    professional = result.scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional not found")

    professional.vetting_status = body.status
    if body.vetting_facility:
        professional.vetting_facility = body.vetting_facility
    await db.commit()
    await db.refresh(professional, ["user"])

    return ProfessionalResponse(
        id=professional.id,
        display_name=professional.user.display_name,
        specialty=professional.specialty,
        tier=professional.tier,
        vetting_status=professional.vetting_status,
        bio=professional.bio,
        years_experience=professional.years_experience,
        languages=professional.languages,
        created_at=professional.created_at,
    )


@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_professional(
    body: AssignRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    prof_result = await db.execute(
        select(Professional).where(
            Professional.id == body.professional_id,
            Professional.vetting_status == "APPROVED",
        )
    )
    professional = prof_result.scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approved professional not found")

    comm_result = await db.execute(select(Community).where(Community.id == body.community_id))
    community = comm_result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    assignment = await assign_professional_to_community(
        professional_id=body.professional_id,
        community_id=body.community_id,
        tier=professional.tier,
        db=db,
    )
    return {"assignment_id": str(assignment.id), "status": "assigned"}


@router.post("/communities", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(
    body: CommunityCreateRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    valid_types = ("ALCOHOL", "DRUGS", "GAMBLING", "GAMING", "SEX", "FOOD", "SMOKING", "OTHER")
    if body.addiction_type not in valid_types:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid addiction_type")
    if body.required_tier and body.required_tier not in ("S", "A", "B"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid required_tier")

    existing = await db.execute(select(Community).where(Community.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")

    community = Community(
        name=body.name,
        slug=body.slug,
        addiction_type=body.addiction_type,
        description=body.description,
        required_tier=body.required_tier,
    )
    db.add(community)
    await db.commit()
    await db.refresh(community)
    return community


@router.get("/communities", response_model=list[CommunityResponse])
async def list_all_communities(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).order_by(Community.name))
    return result.scalars().all()


@router.get("/assignments", response_model=list[dict])
async def list_assignments(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProfessionalAssignment).where(ProfessionalAssignment.is_active == True)
    )
    assignments = result.scalars().all()
    out = []
    for a in assignments:
        await db.refresh(a, ["professional", "community"])
        await db.refresh(a.professional, ["user"])
        out.append({
            "assignment_id": str(a.id),
            "professional_display_name": a.professional.user.display_name,
            "professional_tier": a.professional.tier,
            "community_name": a.community.name,
            "community_slug": a.community.slug,
            "assigned_at": a.assigned_at.isoformat(),
        })
    return out
