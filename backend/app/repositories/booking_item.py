from collections.abc import Sequence
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.booking_item import BookingItem
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.booking_item import BookingItemCreate, BookingItemUpdate


class BookingItemRepository(
    BaseCRUD[BookingItem, BookingItemCreate, BookingItemUpdate],
    SearchableRepository[BookingItem],
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, BookingItem, db)
        SearchableRepository.__init__(self, BookingItem, db)

    async def get_by_booking(self, booking_id: UUID, *, skip: int = 0, limit: int = 100) -> Sequence[BookingItem]:
        return await self.get_multi(skip=skip, limit=limit, booking_id=booking_id)

