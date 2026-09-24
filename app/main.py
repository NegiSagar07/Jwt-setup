from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .db import init_db
from .dependency import get_current_user
from .models.user import User
from .router.auth import router as auth_router
from .router.health import router as health_router
from .schemas.user import UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="JWT Auth Template", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(health_router)


@app.get("/users/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
