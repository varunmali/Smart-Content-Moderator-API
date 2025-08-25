# Smart Content Moderator API

A FastAPI backend for AI-powered text and image content moderation, with Slack/Email notifications and analytics.

## Features

- **Text & Image Moderation**: Detects inappropriate content (toxic, spam, harassment, safe) using AI.  
- **Notifications**: Sends alerts via Slack and email when inappropriate content is detected.  
- **Analytics**: Tracks moderation requests and provides summaries.  
- **Async Backend**: Built with FastAPI and async/await patterns for high performance.  
- **Database**: SQLite-based storage with SQLAlchemy ORM.  

## Technologies

- **Backend Framework**: FastAPI  
- **Database**: SQLite with SQLAlchemy Async ORM  
- **Notifications**: Slack Webhooks, BrevoMail/Sendinblue API  
- **AI/LLM Integration**: Mocked OpenAI API (GPT-4/Gemini ready)  
- **Python Version**: 3.11+  

## Setup Instructions

1. **Clone the repository**  
```
git clone https://github.com/varunmali/Smart-Content-Moderator-API
cd Smart-Content-Moderator-API
```

2. **Create and activate virtual environment**  
```
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a .env file in the project root:
```
DATABASE_URL=sqlite+aiosqlite:///./moderator.db
OPENAI_API_KEY=mock-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
EMAIL_API_KEY=your_email_api_key_here
EMAIL_SENDER=no-reply@yourdomain.com
```

5.**Run the server**
```
uvicorn app.main:app --reload
```
