# app/repositories/slot_inventory.py
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.slot_inventory import SlotInventory
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.slot_inventory import SlotInventoryCreate, SlotInventoryUpdate


class SlotInventoryRepository(
    BaseCRUD[SlotInventory, SlotInventoryCreate, SlotInventoryUpdate],
    SearchableRepository,
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, SlotInventory, db)
        SearchableRepository.__init__(self, SlotInventory, db)

    async def get_by_slot(self, slot_id: UUID):
        """Lấy slot inventory theo slot_id"""
        return await self.get(slot_id)
