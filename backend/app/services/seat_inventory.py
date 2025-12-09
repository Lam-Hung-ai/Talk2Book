from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import CabinType, FareBucketType
from app.models.seat_inventory import SeatInventory
from app.repositories.seat_inventory import SeatInventoryRepository
from app.schemas.seat_inventory import (
    SeatInventoryCreate,
    SeatInventoryRead,
    SeatInventoryUpdate,
)


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


async def create_seat_inventory(
    session: AsyncSession, payload: SeatInventoryCreate
) -> SeatInventoryRead:
    _validate_counts(payload.total_seats, payload.held_seats, payload.sold_seats)

    repo = SeatInventoryRepository(session)
    obj = await repo.create(payload)
    return SeatInventoryRead.model_validate(obj, from_attributes=True)


async def list_seat_inventory(
    session: AsyncSession,
    limit: int,
    offset: int,
    instance_id: UUID | None = None,
) -> tuple[Sequence[SeatInventory], int]:
    query = select(SeatInventory)
    if instance_id:
        query = query.where(SeatInventory.instance_id == instance_id)
    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total = (await session.exec(select(SeatInventory))).all()
    return items, len(total)


async def get_seat_inventory(
    session: AsyncSession, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
) -> SeatInventoryRead | None:
    repo = SeatInventoryRepository(session)
    obj = await repo.get(instance_id, cabin, fare_bucket)
    return SeatInventoryRead.model_validate(obj, from_attributes=True) if obj else None


async def update_seat_inventory(
    session: AsyncSession,
    instance_id: UUID,
    cabin: CabinType,
    fare_bucket: FareBucketType,
    payload: SeatInventoryUpdate,
) -> SeatInventoryRead | None:
    repo = SeatInventoryRepository(session)
    obj = await repo.get(instance_id, cabin, fare_bucket)
    if not obj:
        return None

    data = payload.model_dump(exclude_unset=True)
    _validate_counts(
        data.get("total_seats", obj.total_seats),
        data.get("held_seats", obj.held_seats),
        data.get("sold_seats", obj.sold_seats),
    )

    updated = await repo.update(obj, payload)
    return SeatInventoryRead.model_validate(updated, from_attributes=True)


async def delete_seat_inventory(
    session: AsyncSession, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
) -> bool:
    repo = SeatInventoryRepository(session)
    return await repo.delete(instance_id, cabin, fare_bucket)

