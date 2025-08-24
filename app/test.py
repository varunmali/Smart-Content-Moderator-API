import asyncio
from sqlalchemy import text
from app.database import async_session_maker, init_db
from app.models import ModerationRequest

async def test():
    # Init DB (make sure tables exist)
    await init_db()

    async with async_session_maker() as session:
        # Insert a sample moderation request
        new_request = ModerationRequest(
            content_type="text",
            content_hash="dummyhash123",
            status="pending"
        )
        session.add(new_request)
        await session.commit()

        # Fetch back the rows
        result = await session.execute(text("SELECT * FROM moderation_requests"))
        rows = result.fetchall()
        print("Rows in moderation_requests:", rows)

if __name__ == "__main__":
    asyncio.run(test())
