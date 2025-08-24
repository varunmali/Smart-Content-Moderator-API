from fastapi import APIRouter, Query
from app.schemas import AnalyticsSummaryResponse

router = APIRouter()

@router.get("/api/v1/analytics/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(user: str = Query(..., description="User email")):
    # TODO: Query DB for analytics summary
    return AnalyticsSummaryResponse(total_requests=0, inappropriate_count=0, last_request=None)
