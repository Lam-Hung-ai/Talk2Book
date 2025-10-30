from typing import AsyncGenerator
from sqlmodel import SQLModel

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models import * 

engine = create_async_engine(settings.database_url, echo=True)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    print(settings.database_url)
    asyncio.run(init_db())