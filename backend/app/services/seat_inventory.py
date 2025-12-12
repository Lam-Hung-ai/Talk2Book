from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import CabinType, FareBucketType
from app.models.seat_inventory import SeatInventory
from app.repositories.seat_inventory import SeatInventoryRepository
from app.schemas.seat_inventory import (
    SeatInventoryCreate,
    SeatInventoryRead,
    SeatInventoryUpdate,
)


class SeatInventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SeatInventoryRepository(db)

    @staticmethod
    def _validate_counts(total: int | None, held: int | None, sold: int | None) -> None:
        if total is not None and total < 0:
            raise HTTPException(status_code=400, detail="total_seats must be >= 0")
        if held is not None and held < 0:
            raise HTTPException(status_code=400, detail="held_seats must be >= 0")
        if sold is not None and sold < 0:
            raise HTTPException(status_code=400, detail="sold_seats must be >= 0")
        if total is not None and held is not None and held > total:
            raise HTTPException(status_code=400, detail="held_seats cannot exceed total_seats")
        if total is not None and sold is not None and sold > total:
            raise HTTPException(status_code=400, detail="sold_seats cannot exceed total_seats")

    async def create_inventory(
        self, payload: SeatInventoryCreate
    ) -> SeatInventoryRead:
        self._validate_counts(payload.total_seats, payload.held_seats, payload.sold_seats)
        obj = await self.repo.create(payload)
        return SeatInventoryRead.model_validate(obj, from_attributes=True)

    async def list_inventory(
        self,
        page: int = 1,
        page_size: int = 20,
        instance_id: UUID | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size
        items: Sequence[SeatInventory]

        if instance_id:
            items = await self.repo.search(
                query=str(instance_id),
                search_columns=["instance_id"],
                skip=skip,
                limit=page_size,
                exact_match=True,
                case_sensitive=True,
            )
            total = await self.repo.count_search(
                query=str(instance_id),
                search_columns=["instance_id"],
                exact_match=True,
                case_sensitive=True,
            )
        else:
            stmt_items = await self.db.exec(
                SeatInventory.__table__.select().offset(skip).limit(page_size)
            )
            items = stmt_items.all()
            total = await self.repo.get_count()

        return {
            "items": [SeatInventoryRead.model_validate(i, from_attributes=True) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_inventory(
        self, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
    ) -> SeatInventoryRead:
        obj = await self.repo.get(instance_id, cabin, fare_bucket)
        if not obj:
            raise HTTPException(status_code=404, detail="Seat inventory not found")
        return SeatInventoryRead.model_validate(obj, from_attributes=True)

    async def update_inventory(
        self,
        instance_id: UUID,
        cabin: CabinType,
        fare_bucket: FareBucketType,
        payload: SeatInventoryUpdate,
    ) -> SeatInventoryRead:
        obj = await self.repo.get(instance_id, cabin, fare_bucket)
        if not obj:
            raise HTTPException(status_code=404, detail="Seat inventory not found")

        data = payload.model_dump(exclude_unset=True)
        self._validate_counts(
            data.get("total_seats", obj.total_seats),
            data.get("held_seats", obj.held_seats),
            data.get("sold_seats", obj.sold_seats),
        )

        updated = await self.repo.update(obj, payload)
        return SeatInventoryRead.model_validate(updated, from_attributes=True)

    async def delete_inventory(
        self, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
    ) -> None:
        deleted = await self.repo.delete(instance_id, cabin, fare_bucket)
        if not deleted:
            raise HTTPException(status_code=404, detail="Seat inventory not found")

