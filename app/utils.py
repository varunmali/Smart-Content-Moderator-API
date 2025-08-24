"""
Utility functions for Smart Content Moderator API.
"""
import hashlib, json, logging, httpx, os

# Hash content for deduplication
async def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

# Send Slack notification (async)
async def send_slack_notification(message: str) -> bool:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logging.warning("Slack webhook not configured.")
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.post(webhook_url, json={"text": message})
        return resp.status_code == 200

# Send email notification (stub, async)
async def send_email_notification(email: str, message: str) -> bool:
    # Integrate with Brevo, SMTP, or other provider here
    logging.info(f"Email sent to {email}: {message}")
    return True

# Parse LLM response for classification
async def parse_llm_response(llm_response: dict) -> dict:
    content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "").lower()
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
        "llm_response": llm_response
    }
