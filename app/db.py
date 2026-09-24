from beanie import init_beanie
from pymongo import AsyncMongoClient

from .config import settings

client: AsyncMongoClient = AsyncMongoClient(settings.MONGODB_URI)
database = client[settings.MONGODB_DB_NAME]


async def init_db() -> None:
    """Initialize Beanie with all document models. Call once on startup."""
    from .models.user import User

    await init_beanie(database=database, document_models=[User])


async def check_database_health() -> bool:
    """Ping MongoDB to verify the connection is alive and authenticated."""
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
