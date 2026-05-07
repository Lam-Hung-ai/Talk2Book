# app/services/slot_inventory.py
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.currency import Currency
from app.models.time_slot import TimeSlot
from app.repositories.slot_inventory import SlotInventoryRepository
from app.schemas.slot_inventory import (
    SlotInventoryCreate,
    SlotInventoryRead,
    SlotInventoryUpdate,
)


class SlotInventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SlotInventoryRepository(db)

    async def _ensure_time_slot(self, slot_id: UUID) -> None:
        time_slot = await self.db.get(TimeSlot, slot_id)
        if not time_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Time slot {slot_id} does not exist",
            )

    async def _ensure_currency(self, currency_code: str) -> None:
        currency = await self.db.get(Currency, currency_code.upper())
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency {currency_code} does not exist",
            )

    @staticmethod
    def _validate_counts(capacity: int | None, sold: int | None) -> None:
        if capacity is not None and capacity <= 0:
            raise HTTPException(status_code=400, detail="capacity must be > 0")
        if sold is not None and sold < 0:
            raise HTTPException(status_code=400, detail="sold must be >= 0")
        if capacity is not None and sold is not None and sold > capacity:
            raise HTTPException(status_code=400, detail="sold cannot exceed capacity")

    async def create_slot_inventory(
        self, payload: SlotInventoryCreate
    ) -> SlotInventoryRead:
        await self._ensure_time_slot(payload.slot_id)
        await self._ensure_currency(payload.currency_code)
        self._validate_counts(payload.capacity, payload.sold)

        slot_inventory = await self.repo.create(payload)
        return SlotInventoryRead.model_validate(slot_inventory, from_attributes=True)

    async def list_slot_inventories(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        slot_id: UUID | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size

        if q:
            items = await self.repo.search(
                query=q,
                search_columns=["slot_id", "currency_code"],
                skip=skip,
                limit=page_size,
                exact_match=False,
                case_sensitive=False,
            )
            total = await self.repo.count_search(
                query=q,
                search_columns=["slot_id", "currency_code"],
                exact_match=False,
                case_sensitive=False,
            )
        else:
            filters = {}
            if slot_id:
                filters["slot_id"] = slot_id

            items = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [
                SlotInventoryRead.model_validate(si, from_attributes=True)
                for si in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_slot_inventory(self, slot_id: UUID) -> SlotInventoryRead:
        slot_inventory = await self.repo.get_by_slot(slot_id)
        if not slot_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Slot inventory not found"
            )
        return SlotInventoryRead.model_validate(slot_inventory, from_attributes=True)

    async def update_slot_inventory(
        self, slot_id: UUID, payload: SlotInventoryUpdate
    ) -> SlotInventoryRead:
        slot_inventory = await self.repo.get_by_slot(slot_id)
        if not slot_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Slot inventory not found"
            )

        data = payload.model_dump(exclude_unset=True)

        if "currency_code" in data:
            await self._ensure_currency(data["currency_code"])

        # Validate counts
        capacity = data.get("capacity", slot_inventory.capacity)
        sold = data.get("sold", slot_inventory.sold)
        self._validate_counts(capacity, sold)

        updated = await self.repo.update(slot_inventory, data)
        return SlotInventoryRead.model_validate(updated, from_attributes=True)

    async def delete_slot_inventory(self, slot_id: UUID) -> None:
        slot_inventory = await self.repo.get_by_slot(slot_id)
        if not slot_inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Slot inventory not found"
            )
        await self.repo.delete(slot_id)
