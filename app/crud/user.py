from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId

from ..models.user import User
from ..schemas.user import UserCreate
from ..security import hash_password


async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one(User.email == email)


async def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        object_id = PydanticObjectId(user_id)
    except ValueError:
        return None
    return await User.get(object_id)


async def create_user(user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    await user.insert()
    return user


async def update_password(user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    await user.save()
    return user


async def set_password_reset_otp(user: User, otp: str, expires_at: datetime) -> User:
    user.reset_otp_hash = hash_password(otp)
    user.reset_otp_expires_at = expires_at
    await user.save()
    return user


async def clear_password_reset_otp(user: User) -> User:
    user.reset_otp_hash = None
    user.reset_otp_expires_at = None
    await user.save()
    return user
