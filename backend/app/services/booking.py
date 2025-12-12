from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.booking import BookingRepository
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate


class BookingService:
    def __init__(self, db: AsyncSession):
        self.repo = BookingRepository(db)

    async def create_booking(self, booking_in: BookingCreate) -> BookingRead:
        booking = await self.repo.create(booking_in)
        return BookingRead.model_validate(booking, from_attributes=True)

    async def get_booking(self, booking_id: UUID) -> BookingRead:
        booking = await self.repo.get_or_404(booking_id, detail="Booking not found")
        return BookingRead.model_validate(booking, from_attributes=True)

    async def list_bookings(
        self,
        page: int = 1,
        page_size: int = 50,
        user_id: UUID | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if user_id is not None:
            filters["user_id"] = user_id
        if state is not None:
            filters["state"] = state

        bookings = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [BookingRead.model_validate(b, from_attributes=True) for b in bookings],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_booking(self, booking_id: UUID, booking_in: BookingUpdate) -> BookingRead:
        booking = await self.repo.get_or_404(booking_id, detail="Booking not found")
        updated = await self.repo.update(booking, booking_in)
        return BookingRead.model_validate(updated, from_attributes=True)

    async def delete_booking(self, booking_id: UUID) -> None:
        await self.repo.delete(booking_id)

    async def search_bookings(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        bookings = await self.repo.search(
            query=q,
            search_columns=["state"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["state"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [BookingRead.model_validate(b, from_attributes=True) for b in bookings],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

