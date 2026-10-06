from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import redis_client


async def health_db(session: AsyncSession):
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        await session.rollback()
        raise


async def health_redis():
    try:
        redis_client.execute_command("ping")
        return True
    except Exception:
        return False
        raise
