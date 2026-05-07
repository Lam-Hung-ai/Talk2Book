from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.booking_item import BookingItemRepository
from app.schemas.booking_item import (
    BookingItemCreate,
    BookingItemRead,
    BookingItemUpdate,
)


class BookingItemService:
    def __init__(self, db: AsyncSession):
        self.repo = BookingItemRepository(db)
        self.booking_repo = BookingRepository(db)

    async def create_item(self, item_in: BookingItemCreate) -> BookingItemRead:
        if not await self.booking_repo.get(item_in.booking_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )
        item = await self.repo.create(item_in)
        return BookingItemRead.model_validate(item, from_attributes=True)

    async def get_item(self, item_id: UUID) -> BookingItemRead:
        item = await self.repo.get_or_404(item_id, detail="Booking item not found")
        return BookingItemRead.model_validate(item, from_attributes=True)

    async def list_items(
        self,
        page: int = 1,
        page_size: int = 50,
        booking_id: UUID | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        filters: dict[str, Any] = {}
        if booking_id is not None:
            filters["booking_id"] = booking_id

        items = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                BookingItemRead.model_validate(i, from_attributes=True) for i in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_item(
        self, item_id: UUID, item_in: BookingItemUpdate
    ) -> BookingItemRead:
        item = await self.repo.get_or_404(item_id, detail="Booking item not found")
        updated = await self.repo.update(item, item_in)
        return BookingItemRead.model_validate(updated, from_attributes=True)

    async def delete_item(self, item_id: UUID) -> None:
        await self.repo.delete(item_id)

    async def search_items(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        items = await self.repo.search(
            query=q,
            search_columns=["vertical"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["vertical"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )
        return {
            "items": [
                BookingItemRead.model_validate(i, from_attributes=True) for i in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
