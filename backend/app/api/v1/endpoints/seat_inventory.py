from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models.enums import CabinType, FareBucketType
from app.schemas.seat_inventory import (
    SeatInventoryCreate,
    SeatInventoryRead,
    SeatInventoryUpdate,
)
from app.services.seat_inventory import (
    create_seat_inventory,
    delete_seat_inventory,
    get_seat_inventory,
    list_seat_inventory,
    update_seat_inventory,
)

router = APIRouter()


@router.post(
    "",
    response_model=SeatInventoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_seat_inventory_ep(
    payload: SeatInventoryCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_seat_inventory(session, payload)


@router.get(
    "/",
    response_model=list[SeatInventoryRead],
)
async def list_seat_inventory_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    instance_id: UUID | None = Query(None),
):
    items, _ = await list_seat_inventory(
        session=session, limit=limit, offset=offset, instance_id=instance_id
    )
    return items


@router.get(
    "/{instance_id}/{cabin}/{fare_bucket}",
    response_model=SeatInventoryRead,
)
async def get_seat_inventory_ep(
    instance_id: UUID = Path(...),
    cabin: CabinType = Path(...),
    fare_bucket: FareBucketType = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    obj = await get_seat_inventory(session, instance_id, cabin, fare_bucket)
    if not obj:
        raise HTTPException(status_code=404, detail="Seat inventory not found")
    return obj


@router.put(
    "/{instance_id}/{cabin}/{fare_bucket}",
    response_model=SeatInventoryRead,
)
async def update_seat_inventory_ep(
    payload: SeatInventoryUpdate,
    instance_id: UUID = Path(...),
    cabin: CabinType = Path(...),
    fare_bucket: FareBucketType = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    obj = await update_seat_inventory(session, instance_id, cabin, fare_bucket, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Seat inventory not found")
    return obj


@router.delete(
    "/{instance_id}/{cabin}/{fare_bucket}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_seat_inventory_ep(
    instance_id: UUID = Path(...),
    cabin: CabinType = Path(...),
    fare_bucket: FareBucketType = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_seat_inventory(session, instance_id, cabin, fare_bucket)
    if not ok:
        raise HTTPException(status_code=404, detail="Seat inventory not found")
    return None

