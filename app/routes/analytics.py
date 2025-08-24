from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas import AnalyticsSummaryResponse
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/api/v1/analytics/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    user: str = Query(..., description="User email"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get requests for this user
        stmt = select(models.ModerationRequest).where(models.ModerationRequest.user_email == user)
        requests = (await db.execute(stmt)).scalars().all()
        total_requests = len(requests)

        # Get classification counts for this user
        stmt = (
            select(models.ModerationResult.classification, func.count())
            .join(models.ModerationRequest, models.ModerationResult.request_id == models.ModerationRequest.id)
            .where(models.ModerationRequest.user_email == user)
            .group_by(models.ModerationResult.classification)
        )
        results = (await db.execute(stmt)).all()
        counts = {r[0]: r[1] for r in results}

        # Last request
        last_request = max([r.created_at for r in requests], default=None)

        return AnalyticsSummaryResponse(
            total_requests=total_requests,
            inappropriate_count=counts.get("toxic", 0) + counts.get("spam", 0) + counts.get("harassment", 0),
            last_request=last_request
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Analytics query failed")
