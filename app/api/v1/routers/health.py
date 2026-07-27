import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Verify that the API and database are responding.
    Without the database no endpoint can serve anything useful, so an
    unreachable database means the whole service is in error, not degraded.
    """
    try:
        await db.execute(text("SELECT 1"))
        api_status = "ok"
        db_status = "ok"
        http_status = status.HTTP_200_OK
    except Exception:
        logger.exception("Health check failed: the database is unreachable.")
        api_status = "error"
        db_status = "unavailable"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={"status": api_status, "database": db_status}
    )
