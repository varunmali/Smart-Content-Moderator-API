from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TextModerationRequest, ImageModerationRequest, ModerationResponse
from app.database import get_db
from app import models
import hashlib, logging, json, os, httpx
from datetime import datetime

router = APIRouter()

# Load environment variables
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")

# --- MOCK LLM function ---
async def call_openai_moderation(text: str):
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
    if not SLACK_WEBHOOK_URL:
        logging.warning("SLACK_WEBHOOK_URL not configured. Skipping Slack notification.")
        return False
    async with httpx.AsyncClient() as client:
        payload = {"text": message}
        response = await client.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            logging.error(f"Slack notification failed: {response.text}")
            return False
    logging.info(f"Slack notification sent: {message}")
    return True

async def send_email_notification(to_email: str, message: str):
    if not EMAIL_API_KEY or not EMAIL_SENDER:
        logging.warning("Email API key or sender not configured. Skipping email notification.")
        return False
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": EMAIL_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "sender": {"name": "Smart Moderator", "email": EMAIL_SENDER},
        "to": [{"email": to_email}],
        "subject": "Content Moderation Alert",
        "htmlContent": f"<p>{message}</p>"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code not in (200, 201, 202):
            logging.error(f"Email notification failed: {response.text}")
            return False
    logging.info(f"Email sent to {to_email}: {message}")
    return True

# --- Text Moderation Endpoint ---
@router.post("/moderate/text", response_model=ModerationResponse)
async def moderate_text(
    request: TextModerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        content_hash = hashlib.sha256(request.text.encode()).hexdigest()
        moderation_req = models.ModerationRequest(
            content_type="text",
            content_hash=content_hash,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(moderation_req)
        await db.flush()

        result = await call_openai_moderation(request.text)

        moderation_res = models.ModerationResult(
            request_id=moderation_req.id,
            classification=result["classification"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            llm_response=json.dumps(result["llm_response"])
        )
        db.add(moderation_res)

        # Update request status to completed
        moderation_req.status = "completed"

        # --- Insert into summary table ---
        summary_entry = models.ModerationSummary(
            request_id=moderation_req.id,
            text=request.text,
            classification=result["classification"],
            confidence=result["confidence"],
            notification_status="pending",
            created_at=datetime.utcnow()
        )
        db.add(summary_entry)

        await db.commit()

        # Send notifications if content is not safe
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

            # update summary notification status
            summary_entry.notification_status = "sent"
            await db.commit()  # <-- commit both notif_log + summary update

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

        moderation_res = models.ModerationResult(
            request_id=moderation_req.id,
            classification=result["classification"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            llm_response=json.dumps(result["llm_response"])
        )
        db.add(moderation_res)
        moderation_req.status = "completed"

        # --- Insert into summary table ---
        notification_status = "not_required" if result["classification"] == "safe" else "pending"
        summary_entry = models.ModerationSummary(
            request_id=moderation_req.id,
            text="[image_data]",
            classification=result["classification"],
            confidence=result["confidence"],
            notification_status=notification_status,
            created_at=datetime.utcnow()
        )
        db.add(summary_entry)

        await db.commit()

        return ModerationResponse(**result)

    except Exception as e:
        logging.error(f"Error in image moderation: {e}")
        raise HTTPException(status_code=500, detail="Image moderation failed")
