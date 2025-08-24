"""
Pydantic schemas for Smart Content Moderator API.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime

class TextModerationRequest(BaseModel):
    email: EmailStr
    text: str = Field(..., description="Text to be moderated")

class ImageModerationRequest(BaseModel):
    email: EmailStr
    image_data: str = Field(..., description="Base64-encoded image data")

class ModerationResponse(BaseModel):
    classification: str
    confidence: float
    reasoning: Optional[str]
    llm_response: Any

class AnalyticsSummaryResponse(BaseModel):
    total_requests: int
    inappropriate_count: int
    last_request: Optional[datetime]