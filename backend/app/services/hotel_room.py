# app/services/hotel_room.py
from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import and_, col, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel import Hotel
from app.models.hotel_room import HotelRoom
from app.repositories.hotel_room import HotelRoomRepository
from app.schemas.hotel_room import HotelRoomCreate, HotelRoomRead, HotelRoomUpdate


async def _ensure_hotel(session: AsyncSession, hotel_id: UUID) -> None:
    hotel = await session.get(Hotel, hotel_id)
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hotel {hotel_id} does not exist",
        )


async def create_hotel_room(session: AsyncSession, data: HotelRoomCreate) -> HotelRoomRead:
    await _ensure_hotel(session, data.hotel_id)

    repo = HotelRoomRepository(session)
    # Kiểm tra unique constraint (hotel_id, code) nếu code được cung cấp
    if data.code:
        existing = await repo.db.exec(
            select(HotelRoom).where(
                and_(HotelRoom.hotel_id == data.hotel_id, HotelRoom.code == data.code)
            )
        )
        if existing.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room code '{data.code}' already exists for this hotel",
            )

    room = await repo.create(data.model_dump())
    return HotelRoomRead.model_validate(room, from_attributes=True)


async def list_hotel_rooms(
    session: AsyncSession,
    limit: int,
    offset: int,
    q: str | None = None,
    hotel_id: UUID | None = None,
    min_capacity: int | None = None,
    max_capacity: int | None = None,
) -> tuple[Sequence[HotelRoom], int]:
    repo = HotelRoomRepository(session)

    query = select(HotelRoom)
    if hotel_id:
        query = query.where(HotelRoom.hotel_id == hotel_id)
    if min_capacity is not None:
        query = query.where(HotelRoom.capacity >= min_capacity)
    if max_capacity is not None:
        query = query.where(HotelRoom.capacity <= max_capacity)
    if q:
        like = f"%{q}%"
        conditions = []
        conditions.append(col(HotelRoom.code).ilike(like))
        conditions.append(col(HotelRoom.bed_config).ilike(like))
        query = query.where(or_(*conditions))

    items = (await session.exec(query.offset(offset).limit(limit))).all()
    
    # Count total
    total_query = select(HotelRoom)
    if hotel_id:
        total_query = total_query.where(HotelRoom.hotel_id == hotel_id)
    if min_capacity is not None:
        total_query = total_query.where(HotelRoom.capacity >= min_capacity)
    if max_capacity is not None:
        total_query = total_query.where(HotelRoom.capacity <= max_capacity)
    if q:
        like = f"%{q}%"
        conditions = []
        conditions.append(col(HotelRoom.code).ilike(like))
        conditions.append(col(HotelRoom.bed_config).ilike(like))
        total_query = total_query.where(or_(*conditions))
    total = len((await session.exec(total_query)).all())
    return items, total


async def get_hotel_room_by_id(session: AsyncSession, room_id: UUID) -> HotelRoomRead | None:
    repo = HotelRoomRepository(session)
    room = await repo.get(room_id)
    return HotelRoomRead.model_validate(room, from_attributes=True) if room else None


async def update_hotel_room_by_id(
    session: AsyncSession, room_id: UUID, payload: HotelRoomUpdate
) -> HotelRoomRead | None:
    repo = HotelRoomRepository(session)
    room = await repo.get(room_id)
    if not room:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "hotel_id" in data:
        await _ensure_hotel(session, data["hotel_id"])

    # Kiểm tra unique constraint nếu có update code
    if "code" in data and data["code"]:
        final_hotel_id = data.get("hotel_id", room.hotel_id)
        existing = await repo.db.exec(
            select(HotelRoom).where(
                and_(
                    HotelRoom.hotel_id == final_hotel_id,
                    HotelRoom.code == data["code"],
                    HotelRoom.id != room_id,
                )
            )
        )
        if existing.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room code '{data['code']}' already exists for this hotel",
            )

    updated = await repo.update(room, data)
    return HotelRoomRead.model_validate(updated, from_attributes=True)


async def delete_hotel_room_by_id(session: AsyncSession, room_id: UUID) -> bool:
    repo = HotelRoomRepository(session)
    room = await repo.get(room_id)
    if not room:
        return False
    await repo.delete(room_id)
    return True

