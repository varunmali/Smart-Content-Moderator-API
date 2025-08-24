from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas import TextModerationRequest, ImageModerationRequest, ModerationResponse

router = APIRouter()

@router.post("/api/v1/moderate/text", response_model=ModerationResponse)
async def moderate_text(request: TextModerationRequest, background_tasks: BackgroundTasks):
    # TODO: Integrate LLM, save to DB, send notifications
    return ModerationResponse(classification="safe", confidence=1.0, reasoning="Stub", llm_response={})

@router.post("/api/v1/moderate/image", response_model=ModerationResponse)
async def moderate_image(request: ImageModerationRequest, background_tasks: BackgroundTasks):
    # TODO: Integrate image moderation, save to DB, send notifications
    return ModerationResponse(classification="safe", confidence=1.0, reasoning="Stub", llm_response={})
