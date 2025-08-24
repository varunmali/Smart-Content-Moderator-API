from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas import AnalyticsSummaryResponse
from app.database import get_db
from app import models
from datetime import datetime

router = APIRouter()

@router.get("/api/v1/analytics/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    user: str = Query(..., description="User email"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get all requests for user
        stmt = select(models.ModerationRequest).where(models.ModerationRequest.content_hash != None)
        requests = (await db.execute(stmt)).scalars().all()
        total_requests = len(requests)

        # Get classification counts
        stmt = select(models.ModerationResult.classification, func.count()).group_by(models.ModerationResult.classification)
        results = (await db.execute(stmt)).all()
        counts = {r[0]: r[1] for r in results}

        # Get last request
        last_request = max([r.created_at for r in requests], default=None)

        return AnalyticsSummaryResponse(
            total_requests=total_requests,
            inappropriate_count=counts.get("toxic", 0) + counts.get("spam", 0) + counts.get("harassment", 0),
            last_request=last_request
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analytics query failed")from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas import AnalyticsSummaryResponse
from app.database import get_db
from app import models
from datetime import datetime

router = APIRouter()

@router.get("/api/v1/analytics/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    user: str = Query(..., description="User email"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch all moderation requests for this user
        stmt_requests = select(models.ModerationRequest).where(models.ModerationRequest.email == user)
        requests = (await db.execute(stmt_requests)).scalars().all()
        total_requests = len(requests)

        # Fetch classification counts for this user's requests
        stmt_counts = (
            select(models.ModerationResult.classification, func.count())
            .join(models.ModerationRequest, models.ModerationResult.request_id == models.ModerationRequest.id)
            .where(models.ModerationRequest.email == user)
            .group_by(models.ModerationResult.classification)
        )
        results = (await db.execute(stmt_counts)).all()
        counts = {r[0]: r[1] for r in results}

        # Get the last request timestamp
        last_request = max([r.created_at for r in requests], default=None)

        return AnalyticsSummaryResponse(
            total_requests=total_requests,
            inappropriate_count=counts.get("toxic", 0) + counts.get("spam", 0) + counts.get("harassment", 0),
            last_request=last_request
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics query failed: {str(e)}")
