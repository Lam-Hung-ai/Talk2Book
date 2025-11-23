from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.v1.deps import get_async_session
from app.schemas.hotel_room import (
    HotelRoomCreate,
    HotelRoomRead,
    HotelRoomUpdate,
)
from app.services.hotel_room import (
    create_hotel_room,
    delete_hotel_room_by_id,
    get_hotel_room_by_id,
    list_hotel_rooms,
    update_hotel_room_by_id,
)

router = APIRouter()


@router.post(
    "",
    response_model=HotelRoomRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_hotel_room_ep(
    payload: HotelRoomCreate,
    session: AsyncSession = Depends(get_async_session),
):
    room = await create_hotel_room(session=session, data=payload)
    return room


@router.get(
    "/",
    response_model=list[HotelRoomRead],
)
async def list_hotel_rooms_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, description="Search by code / bed_config"),
    hotel_id: UUID | None = Query(None),
    min_capacity: int | None = Query(None, ge=0),
    max_capacity: int | None = Query(None, ge=0),
):
    items, _total = await list_hotel_rooms(
        session=session,
        limit=limit,
        offset=offset,
        q=q,
        hotel_id=hotel_id,
        min_capacity=min_capacity,
        max_capacity=max_capacity,
    )
    return items


@router.get(
    "/{room_id}",
    response_model=HotelRoomRead,
)
async def get_hotel_room_ep(
    room_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    room = await get_hotel_room_by_id(session, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Hotel room not found")
    return room


@router.put(
    "/{room_id}",
    response_model=HotelRoomRead,
)
async def update_hotel_room_ep(
    room_id: UUID,
    payload: HotelRoomUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    room = await update_hotel_room_by_id(session, room_id, payload)
    if not room:
        raise HTTPException(status_code=404, detail="Hotel room not found")
    return room


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hotel_room_ep(
    room_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_hotel_room_by_id(session, room_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Hotel room not found")
    return None
