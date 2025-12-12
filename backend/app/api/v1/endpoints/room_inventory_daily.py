from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.room_inventory_daily import (
    RoomInventoryDailyCreate,
    RoomInventoryDailyRead,
    RoomInventoryDailyUpdate,
)
from app.services.room_inventory_daily import (
    create_room_inventory_daily,
    delete_room_inventory_daily,
    get_room_inventory_daily_by_id,
    list_room_inventory_daily,
    update_room_inventory_daily,
)

router = APIRouter()


@router.post("", response_model=RoomInventoryDailyRead, status_code=status.HTTP_201_CREATED)
async def create_room_inventory_daily_ep(
    payload: RoomInventoryDailyCreate,
    session: AsyncSession = Depends(get_async_session),
):
    inventory = await create_room_inventory_daily(session, payload)
    return inventory


@router.get("/", response_model=list[RoomInventoryDailyRead])
async def list_room_inventory_daily_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    room_id: UUID | None = Query(None),
    rate_plan_id: UUID | None = Query(None),
    stay_date: date | None = Query(None),
    stay_date_from: date | None = Query(None),
    stay_date_to: date | None = Query(None),
):
    items, _ = await list_room_inventory_daily(
        session=session,
        limit=limit,
        offset=offset,
        room_id=room_id,
        rate_plan_id=rate_plan_id,
        stay_date=stay_date,
        stay_date_from=stay_date_from,
        stay_date_to=stay_date_to,
    )
    return items


@router.get(
    "/{room_id}/{rate_plan_id}/{stay_date}",
    response_model=RoomInventoryDailyRead,
)
async def get_room_inventory_daily_ep(
    room_id: UUID = Path(...),
    rate_plan_id: UUID = Path(...),
    stay_date: date = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    inventory = await get_room_inventory_daily_by_id(session, room_id, rate_plan_id, stay_date)
    if not inventory:
        raise HTTPException(status_code=404, detail="Room inventory not found")
    return inventory


@router.put(
    "/{room_id}/{rate_plan_id}/{stay_date}",
    response_model=RoomInventoryDailyRead,
)
async def update_room_inventory_daily_ep(
    room_id: UUID,
    rate_plan_id: UUID,
    stay_date: date,
    payload: RoomInventoryDailyUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    inventory = await update_room_inventory_daily(
        session, room_id, rate_plan_id, stay_date, payload
    )
    if not inventory:
        raise HTTPException(status_code=404, detail="Room inventory not found")
    return inventory


@router.delete(
    "/{room_id}/{rate_plan_id}/{stay_date}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_room_inventory_daily_ep(
    room_id: UUID,
    rate_plan_id: UUID,
    stay_date: date,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_room_inventory_daily(session, room_id, rate_plan_id, stay_date)
    if not ok:
        raise HTTPException(status_code=404, detail="Room inventory not found")
    return None

