# app/services/room_rate_plan.py
from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import and_, col, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.currency import Currency
from app.models.hotel import Hotel
from app.models.room_rate_plan import RoomRatePlan
from app.repositories.room_rate_plan import RoomRatePlanRepository
from app.schemas.room_rate_plan import RoomRatePlanCreate, RoomRatePlanRead, RoomRatePlanUpdate


async def _ensure_hotel(session: AsyncSession, hotel_id: UUID) -> None:
    hotel = await session.get(Hotel, hotel_id)
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hotel {hotel_id} does not exist",
        )


async def _ensure_currency(session: AsyncSession, currency_code: str) -> None:
    currency = await session.get(Currency, currency_code.upper())
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {currency_code} does not exist",
        )


async def create_room_rate_plan(session: AsyncSession, payload: RoomRatePlanCreate) -> RoomRatePlanRead:
    await _ensure_hotel(session, payload.hotel_id)
    await _ensure_currency(session, payload.currency_code)

    repo = RoomRatePlanRepository(session)
    # Kiểm tra unique constraint (hotel_id, name)
    existing = await repo.db.exec(
        select(RoomRatePlan).where(
            and_(RoomRatePlan.hotel_id == payload.hotel_id, RoomRatePlan.name == payload.name)
        )
    )
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rate plan '{payload.name}' already exists for this hotel",
        )

    data = payload.model_dump()
    data["currency_code"] = payload.currency_code.upper()
    plan = await repo.create(data)
    return RoomRatePlanRead.model_validate(plan, from_attributes=True)


async def list_room_rate_plans(
    session: AsyncSession,
    limit: int,
    offset: int,
    q: str | None = None,
    hotel_id: UUID | None = None,
    currency_code: str | None = None,
) -> tuple[Sequence[RoomRatePlan], int]:
    repo = RoomRatePlanRepository(session)

    query = select(RoomRatePlan)
    if hotel_id:
        query = query.where(RoomRatePlan.hotel_id == hotel_id)
    if currency_code:
        query = query.where(RoomRatePlan.currency_code == currency_code.upper())
    if q:
        like = f"%{q}%"
        conditions = []
        conditions.append(col(RoomRatePlan.name).ilike(like))
        conditions.append(col(RoomRatePlan.meal_plan).ilike(like))
        query = query.where(or_(*conditions))

    items = (await session.exec(query.offset(offset).limit(limit))).all()
    
    # Count total
    total_query = select(RoomRatePlan)
    if hotel_id:
        total_query = total_query.where(RoomRatePlan.hotel_id == hotel_id)
    if currency_code:
        total_query = total_query.where(RoomRatePlan.currency_code == currency_code.upper())
    if q:
        like = f"%{q}%"
        conditions = []
        conditions.append(col(RoomRatePlan.name).ilike(like))
        conditions.append(col(RoomRatePlan.meal_plan).ilike(like))
        total_query = total_query.where(or_(*conditions))
    total = len((await session.exec(total_query)).all())
    return items, total


async def get_room_rate_plan_by_id(session: AsyncSession, rate_plan_id: UUID) -> RoomRatePlanRead | None:
    repo = RoomRatePlanRepository(session)
    plan = await repo.get(rate_plan_id)
    return RoomRatePlanRead.model_validate(plan, from_attributes=True) if plan else None


async def update_room_rate_plan_by_id(
    session: AsyncSession, rate_plan_id: UUID, payload: RoomRatePlanUpdate
) -> RoomRatePlanRead | None:
    repo = RoomRatePlanRepository(session)
    plan = await repo.get(rate_plan_id)
    if not plan:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "hotel_id" in data:
        await _ensure_hotel(session, data["hotel_id"])
    if "currency_code" in data:
        await _ensure_currency(session, data["currency_code"])
        data["currency_code"] = data["currency_code"].upper()

    # Kiểm tra unique constraint nếu có update name
    if "name" in data:
        final_hotel_id = data.get("hotel_id", plan.hotel_id)
        existing = await repo.db.exec(
            select(RoomRatePlan).where(
                and_(
                    RoomRatePlan.hotel_id == final_hotel_id,
                    RoomRatePlan.name == data["name"],
                    RoomRatePlan.id != rate_plan_id,
                )
            )
        )
        if existing.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rate plan '{data['name']}' already exists for this hotel",
            )

    updated = await repo.update(plan, data)
    return RoomRatePlanRead.model_validate(updated, from_attributes=True)


async def delete_room_rate_plan_by_id(session: AsyncSession, rate_plan_id: UUID) -> bool:
    repo = RoomRatePlanRepository(session)
    plan = await repo.get(rate_plan_id)
    if not plan:
        return False
    await repo.delete(rate_plan_id)
    return True

