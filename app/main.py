from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.moderate import router as moderate_router
from app.routes.analytics import router as analytics_router
from app.database import init_db
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Smart Content Moderator API",
    description="Async FastAPI backend for text/image moderation with LLM integration and notifications",
    version="1.0.0",
    openapi_tags=[
        {"name": "Moderation", "description": "Endpoints for text/image moderation"},
        {"name": "Analytics", "description": "Endpoints for analytics & reports"},
    ]
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with version prefix
app.include_router(moderate_router, prefix="/api/v1", tags=["Moderation"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])

@app.on_event("startup")
async def startup():
    logging.info("Starting up Smart Content Moderator API...")
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    logging.info("Shutting down Smart Content Moderator API...")

@app.get("/")
async def root():
    return {"message": "Smart Content Moderator API is running."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
