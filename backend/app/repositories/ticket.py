from collections.abc import Sequence
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.ticket import Ticket
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketRepository(BaseCRUD[Ticket, TicketCreate, TicketUpdate], SearchableRepository[Ticket]):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Ticket, db)
        SearchableRepository.__init__(self, Ticket, db)

    async def get_by_booking_item(self, item_id: UUID, *, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        return await self.get_multi(skip=skip, limit=limit, item_id=item_id)

