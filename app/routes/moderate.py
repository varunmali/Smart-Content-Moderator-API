from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TextModerationRequest, ImageModerationRequest, ModerationResponse
from app.database import get_db
from app import models
import hashlib, logging, os, httpx, json
from datetime import datetime

router = APIRouter()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")  # For Brevo or SMTP

async def call_openai_moderation(text: str):
    # Example OpenAI GPT-4 moderation call
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Classify the following text as toxic, spam, harassment, or safe."},
            {"role": "user", "content": text}
        ]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        # Parse classification from LLM response (customize as needed)
        content = result["choices"][0]["message"]["content"].lower()
        if "toxic" in content:
            classification = "toxic"
        elif "spam" in content:
            classification = "spam"
        elif "harassment" in content:
            classification = "harassment"
        else:
            classification = "safe"
        return {
            "classification": classification,
            "confidence": 0.95,  # Placeholder
            "reasoning": content,
            "llm_response": result
        }

async def send_slack_notification(message: str):
    if not SLACK_WEBHOOK_URL:
        logging.warning("Slack webhook not configured.")
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.post(SLACK_WEBHOOK_URL, json={"text": message})
        return resp.status_code == 200

async def send_email_notification(email: str, message: str):
    # Placeholder for Brevo/SMTP integration
    logging.info(f"Email sent to {email}: {message}")
    return True

@router.post("/api/v1/moderate/text", response_model=ModerationResponse)
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
        await db.flush()  # Get ID

        result = await call_openai_moderation(request.text)
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

        # Notification if inappropriate
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

@router.post("/api/v1/moderate/image", response_model=ModerationResponse)
async def moderate_image(
    request: ImageModerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Placeholder: Replace with actual image moderation API
        content_hash = hashlib.sha256(request.image_data.encode()).hexdigest()
        moderation_req = models.ModerationRequest(
            content_type="image",
            content_hash=content_hash,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(moderation_req)
        await db.flush()

        # Dummy logic: always safe
        result = {
            "classification": "safe",
            "confidence": 1.0,
            "reasoning": "Image moderation not implemented.",
            "llm_response": {}
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
        await db.commit()

        # Notification if inappropriate
        if result["classification"] != "safe":
            msg = f"Inappropriate image detected for {request.email}: {result['classification']}"
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
        logging.error(f"Error in image moderation: {e}")
        raise HTTPException(status_code=500, detail="Image moderation failed")