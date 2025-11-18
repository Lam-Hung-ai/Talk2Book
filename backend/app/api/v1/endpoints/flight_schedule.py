from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import Optional
from uuid import UUID
from datetime import time

from sqlmodel.ext.asyncio.session import AsyncSession
from app.api.v1.deps import get_async_session

from app.schemas.flight_schedule import (
    FlightScheduleRead,
    FlightScheduleCreate,
    FlightScheduleUpdate,
)
from app.services.flight_schedule import (
    create_flight_schedule,
    list_flight_schedules,
    get_flight_schedule_by_id,
    update_flight_schedule_by_id,
    delete_flight_schedule_by_id,
)

router = APIRouter()


@router.post(
    "",
    response_model=FlightScheduleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_flight_schedule_ep(
    payload: FlightScheduleCreate,
    session: AsyncSession = Depends(get_async_session),
):
    schedule = await create_flight_schedule(session, payload)
    return schedule


@router.get(
    "/",
    response_model=list[FlightScheduleRead],
)
async def list_flight_schedules_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, description="Search by flight_number or aircraft_code"),
    provider_id: Optional[UUID] = Query(None),
    route_id: Optional[UUID] = Query(None),
    dow: Optional[int] = Query(None, ge=0, le=6, description="Day of week (0=Mon)"),
):
    items, _ = await list_flight_schedules(
        session=session,
        limit=limit,
        offset=offset,
        q=q,
        provider_id=provider_id,
        route_id=route_id,
        dow=dow,
    )
    return items


@router.get(
    "/{schedule_id}",
    response_model=FlightScheduleRead,
)
async def get_flight_schedule_ep(
    schedule_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    schedule = await get_flight_schedule_by_id(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Flight schedule not found")
    return schedule


@router.put(
    "/{schedule_id}",
    response_model=FlightScheduleRead,
)
async def update_flight_schedule_ep(
    schedule_id: UUID,
    payload: FlightScheduleUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    schedule = await update_flight_schedule_by_id(session, schedule_id, payload)
    if not schedule:
        raise HTTPException(status_code=404, detail="Flight schedule not found")
    return schedule


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_flight_schedule_ep(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_flight_schedule_by_id(session, schedule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Flight schedule not found")
    return None
