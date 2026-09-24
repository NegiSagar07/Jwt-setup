from fastapi import APIRouter, HTTPException, status

from ..db import check_database_health

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    if not await check_database_health():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unreachable",
        )
    return {"status": "ok", "database": "up"}
