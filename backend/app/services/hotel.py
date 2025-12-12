# app/services/hotel.py
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.city import City
from app.models.hotel import Hotel
from app.models.provider import Provider
from app.repositories.hotel import HotelRepository
from app.schemas.hotel import HotelCreate, HotelRead, HotelUpdate


async def _ensure_provider(session: AsyncSession, provider_id: UUID) -> None:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider {provider_id} does not exist",
        )


async def _ensure_city(session: AsyncSession, city_id: UUID) -> None:
    city = await session.get(City, city_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"City {city_id} does not exist",
        )


async def create_hotel(session: AsyncSession, payload: HotelCreate) -> HotelRead:
    await _ensure_provider(session, payload.provider_id)
    await _ensure_city(session, payload.city_id)

    repo = HotelRepository(session)
    hotel = await repo.create(payload.model_dump())
    return HotelRead.model_validate(hotel, from_attributes=True)


async def list_hotels(
    session: AsyncSession,
    limit: int,
    offset: int,
    q: str | None = None,
    provider_id: UUID | None = None,
    city_id: UUID | None = None,
) -> tuple[Sequence[Hotel], int]:
    repo = HotelRepository(session)

    query = select(Hotel)
    if provider_id:
        query = query.where(Hotel.provider_id == provider_id)
    if city_id:
        query = query.where(Hotel.city_id == city_id)
    if q:
        like = f"%{q}%"
        query = query.where(col(Hotel.name).ilike(like))

    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total_query = select(Hotel)
    if provider_id:
        total_query = total_query.where(Hotel.provider_id == provider_id)
    if city_id:
        total_query = total_query.where(Hotel.city_id == city_id)
    if q:
        like = f"%{q}%"
        total_query = total_query.where(col(Hotel.name).ilike(like))
    total = len((await session.exec(total_query)).all())
    return items, total


async def get_hotel_by_id(session: AsyncSession, hotel_id: UUID) -> HotelRead | None:
    repo = HotelRepository(session)
    hotel = await repo.get(hotel_id)
    return HotelRead.model_validate(hotel, from_attributes=True) if hotel else None


async def update_hotel_by_id(
    session: AsyncSession, hotel_id: UUID, payload: HotelUpdate
) -> HotelRead | None:
    repo = HotelRepository(session)
    hotel = await repo.get(hotel_id)
    if not hotel:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "provider_id" in data:
        await _ensure_provider(session, data["provider_id"])
    if "city_id" in data:
        await _ensure_city(session, data["city_id"])

    updated = await repo.update(hotel, data)
    return HotelRead.model_validate(updated, from_attributes=True)


async def delete_hotel_by_id(session: AsyncSession, hotel_id: UUID) -> bool:
    repo = HotelRepository(session)
    hotel = await repo.get(hotel_id)
    if not hotel:
        return False
    await repo.delete(hotel_id)
    return True

