from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def health_db_func(session: AsyncSession):
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        await session.rollback()
        raise
