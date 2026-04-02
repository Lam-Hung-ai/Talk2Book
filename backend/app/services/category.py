from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    @staticmethod
    def _normalize_group_name(group_name: str) -> str:
        return group_name.strip()

    @staticmethod
    def _normalize_value(value: str) -> str:
        return value.strip()

    async def create_category(self, category_in: CategoryCreate) -> CategoryRead:
        data = category_in.model_dump()
        data["group_name"] = self._normalize_group_name(data["group_name"])
        data["value"] = self._normalize_value(data["value"])

        existing = await self.repo.get_by_group_and_value(
            data["group_name"], data["value"]
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Giá trị danh mục đã tồn tại trong nhóm",
            )

        db_obj = await self.repo.create(data)
        return CategoryRead.model_validate(db_obj, from_attributes=True)

    async def get_category_by_id(self, category_id: UUID):
        return await self.repo.get_or_404(category_id, detail="Danh mục không tồn tại")

    async def get_categories_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        group_name: str | None = None,
        is_active: bool | None = None,
        q: str | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        normalized_group_name = self._normalize_group_name(group_name) if group_name else None
        keyword = q.strip() if q else None

        items = await self.repo.get_paginated(
            skip=skip,
            limit=page_size,
            group_name=normalized_group_name,
            is_active=is_active,
            q=keyword,
        )
        total = await self.repo.count_paginated(
            group_name=normalized_group_name,
            is_active=is_active,
            q=keyword,
        )

        return {
            "items": [CategoryRead.model_validate(item, from_attributes=True) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_category(self, category_id: UUID, category_in: CategoryUpdate) -> CategoryRead:
        db_obj = await self.get_category_by_id(category_id)
        update_data = category_in.model_dump(exclude_unset=True)

        if "group_name" in update_data and update_data["group_name"] is not None:
            update_data["group_name"] = self._normalize_group_name(update_data["group_name"])
        if "value" in update_data and update_data["value"] is not None:
            update_data["value"] = self._normalize_value(update_data["value"])

        final_group = update_data.get("group_name", db_obj.group_name)
        final_value = update_data.get("value", db_obj.value)
        existing = await self.repo.get_by_group_and_value(final_group, final_value)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Giá trị danh mục đã tồn tại trong nhóm",
            )

        updated = await self.repo.update(db_obj, update_data)
        return CategoryRead.model_validate(updated, from_attributes=True)

    async def delete_category(self, category_id: UUID) -> None:
        await self.repo.delete(category_id)
