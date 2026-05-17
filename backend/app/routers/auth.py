from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.services import auth_service
from app.utils.email import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(
            db=db,
            email=body.email,
            password=body.password,
            real_name=body.real_name,
            phone=body.phone,
            addiction_types=body.addiction_types,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    # Send verification email (non-blocking — don't fail registration if email fails)
    try:
        if user.verification_token:
            await send_verification_email(user.email, user.verification_token)
    except Exception:
        pass

    tokens = auth_service.issue_tokens(str(user.id))
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.authenticate_user(db=db, email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    tokens = auth_service.issue_tokens(str(user.id))
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await auth_service.refresh_tokens(db=db, refresh_token=body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(**tokens)


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    try:
        await auth_service.verify_email(db=db, token=body.token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Always return 204 — never reveal whether the email exists
    token = await auth_service.initiate_password_reset(db=db, email=body.email)
    if token:
        try:
            await send_password_reset_email(body.email, token)
        except Exception:
            pass


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        await auth_service.complete_password_reset(db=db, token=body.token, new_password=body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
