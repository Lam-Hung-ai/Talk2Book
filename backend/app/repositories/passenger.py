from collections.abc import Sequence
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.passenger import Passenger
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.passenger import PassengerCreate, PassengerUpdate


class PassengerRepository(
    BaseCRUD[Passenger, PassengerCreate, PassengerUpdate],
    SearchableRepository[Passenger],
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Passenger, db)
        SearchableRepository.__init__(self, Passenger, db)

    async def get_by_booking(
        self, booking_id: UUID, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Passenger]:
        return await self.get_multi(skip=skip, limit=limit, booking_id=booking_id)
