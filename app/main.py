from fastapi import FastAPI
from app.routes.moderate import router as moderate_router
from app.routes.analytics import router as analytics_router
from app.database import init_db

app = FastAPI(
    title="Smart Content Moderator API",
    description="Async FastAPI backend for text/image moderation with LLM integration and notifications",
    version="1.0.0"
)

# Include routers with version prefix
app.include_router(moderate_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    # Initialize DB tables
    await init_db()

@app.get("/")
async def root():
    return {"message": "Smart Content Moderator API is running."}
