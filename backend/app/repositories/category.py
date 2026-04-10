from sqlalchemy import or_
from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseCRUD
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseCRUD[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_group_and_value(self, group_name: str, value: str) -> Category | None:
        result = await self.db.exec(
            select(Category).where(
                Category.group_name == group_name,
                Category.value == value,
            )
        )
        return result.first()

    async def get_by_group(
        self,
        group_name: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Category]:
        result = await self.db.exec(
            select(Category)
            .where(Category.group_name == group_name)
            .order_by(col(Category.sort_order).asc(), col(Category.value).asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())

    async def get_paginated(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        group_name: str | None = None,
        is_active: bool | None = None,
        q: str | None = None,
    ) -> list[Category]:
        query = select(Category)

        if group_name:
            query = query.where(Category.group_name == group_name)
        if is_active is not None:
            query = query.where(Category.is_active == is_active)
        if q:
            keyword = f"%{q.lower()}%"
            query = query.where(
                or_(
                    func.lower(Category.group_name).like(keyword),
                    func.lower(Category.value).like(keyword),
                    func.lower(func.coalesce(Category.description, "")).like(keyword),
                )
            )

        query = (
            query.order_by(
                col(Category.group_name).asc(),
                col(Category.sort_order).asc(),
                col(Category.value).asc(),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.exec(query)
        return list(result.all())

    async def count_paginated(
        self,
        *,
        group_name: str | None = None,
        is_active: bool | None = None,
        q: str | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Category)

        if group_name:
            statement = statement.where(Category.group_name == group_name)
        if is_active is not None:
            statement = statement.where(Category.is_active == is_active)
        if q:
            keyword = f"%{q.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Category.group_name).like(keyword),
                    func.lower(Category.value).like(keyword),
                    func.lower(func.coalesce(Category.description, "")).like(keyword),
                )
            )

        result = await self.db.exec(statement)
        return result.one()
