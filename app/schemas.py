from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime

class TextModerationRequest(BaseModel):
    email: EmailStr
    text: str

class ImageModerationRequest(BaseModel):
    email: EmailStr
    image_data: str  # base64 encoded

class ModerationResponse(BaseModel):
    classification: str
    confidence: float
    reasoning: Optional[str]
    llm_response: Any

class AnalyticsSummaryResponse(BaseModel):
    total_requests: int
    inappropriate_count: int
    last_request: Optional[datetime]
