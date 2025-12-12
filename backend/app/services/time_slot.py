# app/services/time_slot.py
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.product import Product
from app.models.time_slot import TimeSlot
from app.repositories.time_slot import TimeSlotRepository
from app.schemas.time_slot import TimeSlotCreate, TimeSlotRead, TimeSlotUpdate


class TimeSlotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TimeSlotRepository(db)

    async def _ensure_product(self, product_id: UUID) -> None:
        product = await self.db.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product_id} does not exist",
            )

    @staticmethod
    def _validate_datetimes(start: datetime, end: datetime) -> None:
        if start >= end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_datetime must be earlier than end_datetime",
            )

    async def create_time_slot(self, payload: TimeSlotCreate) -> TimeSlotRead:
        await self._ensure_product(payload.product_id)
        self._validate_datetimes(payload.start_datetime, payload.end_datetime)

        time_slot = await self.repo.create(payload)
        return TimeSlotRead.model_validate(time_slot, from_attributes=True)

    async def list_time_slots(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        product_id: UUID | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size

        if q:
            items = await self.repo.search(
                query=q,
                search_columns=["product_id"],
                skip=skip,
                limit=page_size,
                exact_match=False,
                case_sensitive=False,
            )
            total = await self.repo.count_search(
                query=q,
                search_columns=["product_id"],
                exact_match=False,
                case_sensitive=False,
            )
        else:
            filters = {}
            if product_id:
                filters["product_id"] = product_id

            items = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [TimeSlotRead.model_validate(ts, from_attributes=True) for ts in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_time_slot(self, time_slot_id: UUID) -> TimeSlotRead:
        time_slot = await self.repo.get_or_404(time_slot_id, detail="Time slot not found")
        return TimeSlotRead.model_validate(time_slot, from_attributes=True)

    async def update_time_slot(
        self, time_slot_id: UUID, payload: TimeSlotUpdate
    ) -> TimeSlotRead:
        time_slot = await self.repo.get_or_404(time_slot_id, detail="Time slot not found")
        data = payload.model_dump(exclude_unset=True)

        if "product_id" in data:
            await self._ensure_product(data["product_id"])

        # Validate datetime if either is updated
        start_dt = data.get("start_datetime", time_slot.start_datetime)
        end_dt = data.get("end_datetime", time_slot.end_datetime)
        self._validate_datetimes(start_dt, end_dt)

        updated = await self.repo.update(time_slot, data)
        return TimeSlotRead.model_validate(updated, from_attributes=True)

    async def delete_time_slot(self, time_slot_id: UUID) -> None:
        await self.repo.delete(time_slot_id)

