from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.booking import Booking
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingRepository(
    BaseCRUD[Booking, BookingCreate, BookingUpdate], SearchableRepository[Booking]
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Booking, db)
        SearchableRepository.__init__(self, Booking, db)

    async def get_by_user(
        self, user_id: str, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Booking]:
        return await self.get_multi(skip=skip, limit=limit, user_id=user_id)

    async def get_by_state(
        self, state: str, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Booking]:
        return await self.get_multi(skip=skip, limit=limit, state=state)
