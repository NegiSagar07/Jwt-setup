import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import settings
from ..crud.user import (
    clear_password_reset_otp,
    create_user,
    get_user_by_email,
    set_password_reset_otp,
    update_password,
)
from ..dependency import get_current_user
from ..email import send_password_reset_otp_email
from ..models.user import User
from ..schemas.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserResponse,
)
from ..security import (
    create_access_token,
    generate_otp,
    utcnow_naive,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate):
    existing_user = await get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await create_user(user_in)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Same error for both "no such user" and "wrong password" to avoid
        # leaking which emails are registered.
        raise invalid_credentials

    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    if payload.old_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the old password",
        )

    await update_password(current_user, payload.new_password)
    return MessageResponse(message="Password updated successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest):
    # Always return the same generic message whether or not the email is
    # registered, so this endpoint can't be used to enumerate accounts.
    generic_message = MessageResponse(
        message="If that email is registered, a password reset code has been sent."
    )

    user = await get_user_by_email(payload.email)
    if not user:
        return generic_message

    otp = generate_otp()
    expires_at = utcnow_naive() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    await set_password_reset_otp(user, otp, expires_at)

    try:
        await send_password_reset_otp_email(user.email, otp)
    except Exception:
        # Don't let an email-provider failure (bad SMTP creds, provider
        # outage, etc.) turn into a 500 or leak details to the caller —
        # that would also defeat the point of the generic response above.
        # Log it server-side so it's actually visible to whoever runs this.
        logger.exception("Failed to send password reset OTP email to %s", user.email)

    return generic_message


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest):
    invalid_otp = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset code",
    )

    user = await get_user_by_email(payload.email)
    if not user or not user.reset_otp_hash or not user.reset_otp_expires_at:
        raise invalid_otp

    if utcnow_naive() > user.reset_otp_expires_at:
        await clear_password_reset_otp(user)
        raise invalid_otp

    if not verify_password(payload.otp, user.reset_otp_hash):
        raise invalid_otp

    await update_password(user, payload.new_password)
    await clear_password_reset_otp(user)

    return MessageResponse(message="Password reset successfully")
