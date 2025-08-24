# Smart Content Moderator API

A FastAPI-based backend for content moderation using AI, with notifications and analytics.

## Features
- Moderate text and images for inappropriate content
- Async database (SQLite)
- Slack/Email notifications
- Analytics endpoint

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints
- `POST /api/v1/moderate/text`
- `POST /api/v1/moderate/image`
- `GET /api/v1/analytics/summary?user=email`

## Database Models
- moderation_requests
- moderation_results
- notification_logs

## Environment Variables
- `OPENAI_API_KEY` for LLM integration
- `SLACK_WEBHOOK_URL` for Slack notifications
- `EMAIL_API_KEY` for email notifications

---
