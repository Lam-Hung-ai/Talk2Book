from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.hotel import HotelCreate, HotelRead
from app.service.hotel import create_hotel

router = APIRouter()


@router.post(
    "",
    response_model=HotelRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_hotel_ep(
    payload: HotelCreate, session: AsyncSession = Depends(get_async_session)
):
    hotel = await create_hotel(session=session, data=payload)
    return hotel


@router.get("/", response_model=list[HotelRead])
async def list_hotels_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, description="Search by name/address "),
    city_id: Optional[UUID] = Query(None),
    provider_id: Optional[UUID] = Query(None),
    min_star: Optional[float] = Query(None, ge=0, le=5),
    max_star: Optional[float] = Query(None, ge=0, le=5),
):
    items, _total = await list_hotels(
        session=session,
        limit=limit,
        offset=offset,
        q=q,
        city_id=city_id,
        provider_id=provider_id,
        min_star=min_star,
        max_star=max_star,
    )
    return items


@router.get(
    "/{hotel_id}",
    response_model=HotelRead,
)
async def get_hotel_ep(
    hotel_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    hotel = await get_hotel_by_id(session, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


@router.put(
    "/{hotel_id}",
    response_model=HotelRead,
)
async def update_hotel_ep(
    hotel_id: UUID,
    payload: HotelUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    hotel = await update_hotel_by_id(session, hotel_id, payload)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


@router.delete(
    "/{hotel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hotel_ep(
    hotel_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    deleted = await delete_hotel_by_id(session, hotel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return None
