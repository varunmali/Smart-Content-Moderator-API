
from fastapi import FastAPI
from app.routes.moderate import router as moderate_router
from app.routes.analytics import router as analytics_router
from app.database import engine
from app import models

app = FastAPI()

app.include_router(moderate_router)
app.include_router(analytics_router)

@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Smart Content Moderator API is running."}
