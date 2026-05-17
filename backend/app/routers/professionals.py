from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin, require_professional
from app.models.professional import Professional
from app.models.user import User
from app.schemas.community import CommunityResponse
from app.schemas.professional import ProfessionalEnrollRequest, ProfessionalResponse, VetRequest
from app.services.matching_service import (
    assign_professional_to_community,
    get_communities_for_professional,
)

router = APIRouter(prefix="/professionals", tags=["professionals"])


@router.get("", response_model=list[ProfessionalResponse])
async def list_professionals(
    tier: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Professional).where(Professional.vetting_status == "APPROVED")
    if tier:
        query = query.where(Professional.tier == tier)
    result = await db.execute(query.order_by(Professional.tier))
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


@router.post("/enroll", response_model=ProfessionalResponse, status_code=status.HTTP_201_CREATED)
async def enroll(
    body: ProfessionalEnrollRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Professional).where(Professional.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already enrolled")

    if body.specialty not in ("PSYCHIATRIST", "PSYCHOLOGIST", "COUNSELOR", "THERAPIST", "ADVISOR"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid specialty")
    if body.tier not in ("S", "A", "B"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid tier")

    professional = Professional(
        user_id=current_user.id,
        license_number=body.license_number,
        specialty=body.specialty,
        tier=body.tier,
        vetting_facility=body.vetting_facility,
        bio=body.bio,
        years_experience=body.years_experience,
        languages=body.languages,
    )
    db.add(professional)
    current_user.role = "PROFESSIONAL"
    await db.commit()
    await db.refresh(professional)

    return ProfessionalResponse(
        id=professional.id,
        display_name=current_user.display_name,
        specialty=professional.specialty,
        tier=professional.tier,
        vetting_status=professional.vetting_status,
        bio=professional.bio,
        years_experience=professional.years_experience,
        languages=professional.languages,
        created_at=professional.created_at,
    )


@router.get("/me", response_model=ProfessionalResponse)
async def get_my_profile(current_user: User = Depends(require_professional), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Professional).where(Professional.user_id == current_user.id))
    professional = result.scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional profile not found")
    return ProfessionalResponse(
        id=professional.id,
        display_name=current_user.display_name,
        specialty=professional.specialty,
        tier=professional.tier,
        vetting_status=professional.vetting_status,
        bio=professional.bio,
        years_experience=professional.years_experience,
        languages=professional.languages,
        created_at=professional.created_at,
    )


@router.get("/me/groups", response_model=list[CommunityResponse])
async def get_my_groups(
    current_user: User = Depends(require_professional),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Professional).where(Professional.user_id == current_user.id))
    professional = result.scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional profile not found")
    communities = await get_communities_for_professional(professional.id, db)
    return communities


@router.put("/{professional_id}/vet", response_model=ProfessionalResponse)
async def vet_professional(
    professional_id: str,
    body: VetRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if body.status not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status")

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
