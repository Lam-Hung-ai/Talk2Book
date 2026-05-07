# app/api/v1/deps.py
from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.init_db import async_session


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
