from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.airport import AirportCreate, AirportRead, AirportUpdate
from app.services.airport import (
    create_airport,
    delete_airport,
    list_airports,
    update_airport,
)

router = APIRouter(prefix="/airport", tags=["Airport"])


@router.post("/airports", response_model=AirportRead, status_code=201)
async def create_airport_ep(
    payload: AirportCreate, session: AsyncSession = Depends(get_async_session)
):
    return await create_airport(
        session,
        iata=payload.iata,
        icao=payload.icao,
        city_id=payload.city_id,
        name=payload.name,
        timezone=payload.timezone,
    )


@router.get("/airports", response_model=list[AirportRead])
async def list_airports_ep(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    city_id: Optional[UUID] = None,
    country_code: Optional[str] = None,
    q: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
):
    items, total = await list_airports(
        session,
        limit=limit,
        offset=offset,
        city_id=city_id,
        country_code=country_code,
        q=q,
    )
    return items


@router.patch("/airports/{iata}", response_model=AirportRead)
async def update_airport_ep(
    iata: str,
    payload: AirportUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    return await update_airport(
        session,
        iata=iata,
        icao=payload.icao,
        name=payload.name,
        timezone=payload.timezone,
    )


@router.delete("/airports/{iata}", status_code=204)
async def delete_airport_ep(
    iata: str, session: AsyncSession = Depends(get_async_session)
):
    await delete_airport(session, iata)
