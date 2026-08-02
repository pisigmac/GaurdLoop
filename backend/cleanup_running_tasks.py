import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import update
from sqlalchemy.sql import func
from app.models.task import Task

DB_URL = "postgresql+asyncpg://guardloop:guardloop@localhost:35432/guardloop"

async def cleanup():
    engine = create_async_engine(DB_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        stmt = (
            update(Task)
            .where(Task.status == "running")
            .values(status="completed", completed_at=func.now())
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Cleaned up {result.rowcount} running tasks -> marked as completed.")

if __name__ == "__main__":
    asyncio.run(cleanup())
