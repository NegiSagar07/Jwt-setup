from datetime import datetime, timezone
from typing import Optional

from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing_extensions import Annotated


class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Password-reset OTP (hashed, never stored in plaintext). Both are
    # cleared after a successful reset or once the OTP expires.
    reset_otp_hash: Optional[str] = None
    reset_otp_expires_at: Optional[datetime] = None

    class Settings:
        name = "users"
