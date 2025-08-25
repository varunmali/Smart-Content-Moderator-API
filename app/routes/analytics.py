from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas import AnalyticsSummaryResponse
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/api/v1/analytics/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    db: AsyncSession = Depends(get_db)
):
    try:
        # Total moderation requests
        stmt_total = select(func.count()).select_from(models.ModerationRequest)
        total_requests = (await db.execute(stmt_total)).scalar_one()

        # Count of classifications
        stmt_class = (
            select(models.ModerationResult.classification, func.count())
            .group_by(models.ModerationResult.classification)
        )
        results = (await db.execute(stmt_class)).all()
        counts = {r[0]: r[1] for r in results}

        # Count of notifications by status
        stmt_notif = (
            select(models.NotificationLog.status, func.count())
            .group_by(models.NotificationLog.status)
        )
        notif_counts = (await db.execute(stmt_notif)).all()
        notif_status = {r[0]: r[1] for r in notif_counts}

        # Last request timestamp
        stmt_last = select(func.max(models.ModerationRequest.created_at))
        last_request = (await db.execute(stmt_last)).scalar_one()

        return AnalyticsSummaryResponse(
            total_requests=total_requests,
            inappropriate_count=counts.get("toxic", 0) + counts.get("spam", 0) + counts.get("harassment", 0),
            last_request=last_request,
            notifications_status=notif_status
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics query failed: {e}")
