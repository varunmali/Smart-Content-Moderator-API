"""
Async SQLAlchemy database setup for FastAPI.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./moderator.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create async sessionmaker
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependency for FastAPI endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Async table creation (call on startup)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)