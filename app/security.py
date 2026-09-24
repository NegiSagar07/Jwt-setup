import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# bcrypt only uses the first 72 bytes of input; truncate explicitly so
# longer passwords don't silently lose their tail.
_MAX_PASSWORD_BYTES = 72

_OTP_DIGITS = "0123456789"
_OTP_LENGTH = 6


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def generate_otp() -> str:
    return "".join(secrets.choice(_OTP_DIGITS) for _ in range(_OTP_LENGTH))


def utcnow_naive() -> datetime:
    """UTC 'now' with tzinfo stripped.

    MongoDB stores datetimes as naive UTC and hands them back naive on
    read, so anything that gets persisted and later compared (like the
    OTP expiry) must be generated and compared in this same naive form,
    or the comparison raises when mixed with an aware datetime.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
