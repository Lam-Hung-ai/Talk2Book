from typing import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.core.db import engine

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session