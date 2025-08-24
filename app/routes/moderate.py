from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TextModerationRequest, ImageModerationRequest, ModerationResponse
from app.database import get_db
from app import models
import hashlib, logging, json
from datetime import datetime

router = APIRouter()
SLACK_WEBHOOK_URL = None  # You can configure later
EMAIL_API_KEY = None      # You can configure later

# --- MOCK LLM function ---
async def call_openai_moderation(text: str):
    """
    Mock AI moderation: Classifies text as 'safe' or 'toxic' based on simple keyword checks.
    Replace this later with real OpenAI API if available.
    """
    if any(word in text.lower() for word in ["bad", "hate", "spam", "abuse"]):
        classification = "toxic"
        reasoning = "Detected inappropriate content."
    else:
        classification = "safe"
        reasoning = "No inappropriate content detected."

    return {
        "classification": classification,
        "confidence": 0.95,
        "reasoning": reasoning,
        "llm_response": {"mock": True}
    }

# --- Notification functions ---
async def send_slack_notification(message: str):
    logging.info(f"Slack notification: {message}")
    return True

async def send_email_notification(email: str, message: str):
    logging.info(f"Email sent to {email}: {message}")
    return True

# --- Text Moderation Endpoint ---
@router.post("/moderate/text", response_model=ModerationResponse)
async def moderate_text(
    request: TextModerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Save request in DB
        content_hash = hashlib.sha256(request.text.encode()).hexdigest()
        moderation_req = models.ModerationRequest(
            content_type="text",
            content_hash=content_hash,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(moderation_req)
        await db.flush()

        # Call mock moderation
        result = await call_openai_moderation(request.text)

        # Save result in DB
        moderation_res = models.ModerationResult(
            request_id=moderation_req.id,
            classification=result["classification"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            llm_response=json.dumps(result["llm_response"])
        )
        db.add(moderation_res)
        moderation_req.status = "completed"
        await db.commit()

        # Send notifications if not safe
        if result["classification"] != "safe":
            msg = f"Inappropriate content detected for {request.email}: {result['classification']}"
            background_tasks.add_task(send_slack_notification, msg)
            background_tasks.add_task(send_email_notification, request.email, msg)

            notif_log = models.NotificationLog(
                request_id=moderation_req.id,
                channel="slack/email",
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(notif_log)
            await db.commit()

        return ModerationResponse(**result)

    except Exception as e:
        logging.error(f"Error in text moderation: {e}")
        raise HTTPException(status_code=500, detail="Moderation failed")

# --- Image Moderation Endpoint ---
@router.post("/moderate/image", response_model=ModerationResponse)
async def moderate_image(
    request: ImageModerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Save request in DB
        content_hash = hashlib.sha256(request.image_data.encode()).hexdigest()
        moderation_req = models.ModerationRequest(
            content_type="image",
            content_hash=content_hash,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(moderation_req)
        await db.flush()

        # Mock: all images are safe
        result = {
            "classification": "safe",
            "confidence": 1.0,
            "reasoning": "Image moderation not implemented (mock).",
            "llm_response": {"mock": True}
        }

        # Save result in DB
        moderation_res = models.ModerationResult(
            request_id=moderation_req.id,
            classification=result["classification"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            llm_response=json.dumps(result["llm_response"])
        )
        db.add(moderation_res)
        moderation_req.status = "completed"
        await db.commit()

        return ModerationResponse(**result)

    except Exception as e:
        logging.error(f"Error in image moderation: {e}")
        raise HTTPException(status_code=500, detail="Image moderation failed")
