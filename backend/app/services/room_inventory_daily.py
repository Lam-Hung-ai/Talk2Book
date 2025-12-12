# app/services/room_inventory_daily.py
from collections.abc import Sequence
from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel_room import HotelRoom
from app.models.room_inventory_daily import RoomInventoryDaily
from app.models.room_rate_plan import RoomRatePlan
from app.repositories.room_inventory_daily import RoomInventoryDailyRepository
from app.schemas.room_inventory_daily import (
    RoomInventoryDailyCreate,
    RoomInventoryDailyRead,
    RoomInventoryDailyUpdate,
)


async def _ensure_hotel_room(session: AsyncSession, room_id: UUID) -> None:
    room = await session.get(HotelRoom, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hotel room {room_id} does not exist",
        )


async def _ensure_rate_plan(session: AsyncSession, rate_plan_id: UUID) -> None:
    rate_plan = await session.get(RoomRatePlan, rate_plan_id)
    if not rate_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rate plan {rate_plan_id} does not exist",
        )


async def create_room_inventory_daily(
    session: AsyncSession, payload: RoomInventoryDailyCreate
) -> RoomInventoryDailyRead:
    await _ensure_hotel_room(session, payload.room_id)
    await _ensure_rate_plan(session, payload.rate_plan_id)

    repo = RoomInventoryDailyRepository(session)
    # Kiểm tra unique constraint (room_id, rate_plan_id, stay_date)
    existing = await repo.db.exec(
        select(RoomInventoryDaily).where(
            and_(
                RoomInventoryDaily.room_id == payload.room_id,
                RoomInventoryDaily.rate_plan_id == payload.rate_plan_id,
                RoomInventoryDaily.stay_date == payload.stay_date,
            )
        )
    )
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Inventory already exists for room {payload.room_id}, rate plan {payload.rate_plan_id}, date {payload.stay_date}",
        )

    inventory = await repo.create(payload.model_dump())
    return RoomInventoryDailyRead.model_validate(inventory, from_attributes=True)


async def list_room_inventory_daily(
    session: AsyncSession,
    limit: int,
    offset: int,
    room_id: UUID | None = None,
    rate_plan_id: UUID | None = None,
    stay_date: date | None = None,
    stay_date_from: date | None = None,
    stay_date_to: date | None = None,
) -> tuple[Sequence[RoomInventoryDaily], int]:
    repo = RoomInventoryDailyRepository(session)

    query = select(RoomInventoryDaily)
    if room_id:
        query = query.where(RoomInventoryDaily.room_id == room_id)
    if rate_plan_id:
        query = query.where(RoomInventoryDaily.rate_plan_id == rate_plan_id)
    if stay_date:
        query = query.where(RoomInventoryDaily.stay_date == stay_date)
    if stay_date_from:
        query = query.where(RoomInventoryDaily.stay_date >= stay_date_from)
    if stay_date_to:
        query = query.where(RoomInventoryDaily.stay_date <= stay_date_to)

    items = (await session.exec(query.offset(offset).limit(limit))).all()
    
    # Count total
    total_query = select(RoomInventoryDaily)
    if room_id:
        total_query = total_query.where(RoomInventoryDaily.room_id == room_id)
    if rate_plan_id:
        total_query = total_query.where(RoomInventoryDaily.rate_plan_id == rate_plan_id)
    if stay_date:
        total_query = total_query.where(RoomInventoryDaily.stay_date == stay_date)
    if stay_date_from:
        total_query = total_query.where(RoomInventoryDaily.stay_date >= stay_date_from)
    if stay_date_to:
        total_query = total_query.where(RoomInventoryDaily.stay_date <= stay_date_to)
    total = len((await session.exec(total_query)).all())
    return items, total


async def get_room_inventory_daily_by_id(
    session: AsyncSession, room_id: UUID, rate_plan_id: UUID, stay_date: date
) -> RoomInventoryDailyRead | None:
    repo = RoomInventoryDailyRepository(session)
    result = await repo.db.exec(
        select(RoomInventoryDaily).where(
            and_(
                RoomInventoryDaily.room_id == room_id,
                RoomInventoryDaily.rate_plan_id == rate_plan_id,
                RoomInventoryDaily.stay_date == stay_date,
            )
        )
    )
    inventory = result.first()
    return RoomInventoryDailyRead.model_validate(inventory, from_attributes=True) if inventory else None


async def update_room_inventory_daily(
    session: AsyncSession,
    room_id: UUID,
    rate_plan_id: UUID,
    stay_date: date,
    payload: RoomInventoryDailyUpdate,
) -> RoomInventoryDailyRead | None:
    repo = RoomInventoryDailyRepository(session)
    result = await repo.db.exec(
        select(RoomInventoryDaily).where(
            and_(
                RoomInventoryDaily.room_id == room_id,
                RoomInventoryDaily.rate_plan_id == rate_plan_id,
                RoomInventoryDaily.stay_date == stay_date,
            )
        )
    )
    inventory = result.first()
    if not inventory:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "room_id" in data:
        await _ensure_hotel_room(session, data["room_id"])
    if "rate_plan_id" in data:
        await _ensure_rate_plan(session, data["rate_plan_id"])

    # Kiểm tra unique constraint nếu có update các trường primary key
    if "room_id" in data or "rate_plan_id" in data or "stay_date" in data:
        final_room_id = data.get("room_id", inventory.room_id)
        final_rate_plan_id = data.get("rate_plan_id", inventory.rate_plan_id)
        final_stay_date = data.get("stay_date", inventory.stay_date)
        
        # Nếu thay đổi primary key, kiểm tra xem có conflict không
        if (
            final_room_id != inventory.room_id
            or final_rate_plan_id != inventory.rate_plan_id
            or final_stay_date != inventory.stay_date
        ):
            existing_result = await repo.db.exec(
                select(RoomInventoryDaily).where(
                    and_(
                        RoomInventoryDaily.room_id == final_room_id,
                        RoomInventoryDaily.rate_plan_id == final_rate_plan_id,
                        RoomInventoryDaily.stay_date == final_stay_date,
                    )
                )
            )
            existing = existing_result.first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Inventory already exists for the new combination",
                )

    updated = await repo.update(inventory, data)
    return RoomInventoryDailyRead.model_validate(updated, from_attributes=True)


async def delete_room_inventory_daily(
    session: AsyncSession, room_id: UUID, rate_plan_id: UUID, stay_date: date
) -> bool:
    repo = RoomInventoryDailyRepository(session)
    result = await repo.db.exec(
        select(RoomInventoryDaily).where(
            and_(
                RoomInventoryDaily.room_id == room_id,
                RoomInventoryDaily.rate_plan_id == rate_plan_id,
                RoomInventoryDaily.stay_date == stay_date,
            )
        )
    )
    inventory = result.first()
    if not inventory:
        return False
    
    # Delete by composite key
    await repo.db.delete(inventory)
    await repo.db.commit()
    return True

