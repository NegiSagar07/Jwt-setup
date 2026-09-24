from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from .config import settings
from .crud.user import get_user_by_id
from .models.user import User
from .security import oauth2_scheme


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
    except JWTError:
        raise credential_exception

    user = await get_user_by_id(user_id)
    if user is None:
        raise credential_exception

    return user
