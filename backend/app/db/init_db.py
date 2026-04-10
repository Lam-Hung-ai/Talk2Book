from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models import *

engine = create_async_engine(settings.database_url, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def create_role() -> None:
    DEFAULT_ROLES = ["admin", "user"]
    async with async_session() as db:
        for role_code in DEFAULT_ROLES:
            role = (await db.exec(select(Role).where(Role.code == role_code))).all()

            if not role:
                role = Role(code=role_code)
                db.add(role)
                await db.commit()
                await db.refresh(role)

        await db.commit()

async def create_super_user() -> None:
    pass

async def main() -> None:
    await create_tables()
    await create_role()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
