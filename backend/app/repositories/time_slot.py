# app/repositories/time_slot.py
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.time_slot import TimeSlot
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.time_slot import TimeSlotCreate, TimeSlotUpdate


class TimeSlotRepository(BaseCRUD[TimeSlot, TimeSlotCreate, TimeSlotUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, TimeSlot, db)
        SearchableRepository.__init__(self, TimeSlot, db)

    async def get_by_product_id(self, product_id: UUID) -> list[TimeSlot]:
        """Lấy danh sách time_slots theo product_id"""
        result = await self.db.exec(select(TimeSlot).where(TimeSlot.product_id == product_id))
        return list(result.all())

