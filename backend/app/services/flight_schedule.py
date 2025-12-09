from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.flight_schedule import FlightSchedule
from app.models.provider import Provider
from app.models.route import Route
from app.repositories.flight_schedule import FlightScheduleRepository
from app.schemas.flight_schedule import (
    FlightScheduleCreate,
    FlightScheduleRead,
    FlightScheduleUpdate,
)


async def _ensure_provider(session: AsyncSession, provider_id: UUID) -> None:
    provider = await session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider {provider_id} does not exist",
        )


async def _ensure_route(session: AsyncSession, route_id: UUID) -> None:
    route = await session.get(Route, route_id)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Route {route_id} does not exist",
        )


async def create_flight_schedule(
    session: AsyncSession, payload: FlightScheduleCreate
) -> FlightScheduleRead:
    await _ensure_provider(session, payload.provider_id)
    await _ensure_route(session, payload.route_id)

    repo = FlightScheduleRepository(session)
    schedule = await repo.create(payload)
    return FlightScheduleRead.model_validate(schedule, from_attributes=True)


async def list_flight_schedules(
    session: AsyncSession,
    limit: int,
    offset: int,
    q: str | None = None,
    provider_id: UUID | None = None,
    route_id: UUID | None = None,
    dow: int | None = None,
) -> tuple[Sequence[FlightSchedule], int]:
    repo = FlightScheduleRepository(session)

    if q:
        items = await repo.search(
            query=q,
            search_columns=["flight_number", "aircraft_code"],
            skip=offset,
            limit=limit,
        )
    else:
        items = await repo.list_filtered(
            limit=limit, offset=offset, provider_id=provider_id, route_id=route_id, dow=dow
        )

    total = (await session.exec(select(FlightSchedule))).all()
    return items, len(total)


async def get_flight_schedule_by_id(
    session: AsyncSession, schedule_id: UUID
) -> FlightScheduleRead | None:
    repo = FlightScheduleRepository(session)
    schedule = await repo.get(schedule_id)
    return (
        FlightScheduleRead.model_validate(schedule, from_attributes=True)
        if schedule
        else None
    )


async def update_flight_schedule_by_id(
    session: AsyncSession, schedule_id: UUID, payload: FlightScheduleUpdate
) -> FlightScheduleRead | None:
    repo = FlightScheduleRepository(session)
    schedule = await repo.get(schedule_id)
    if not schedule:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "provider_id" in data:
        await _ensure_provider(session, data["provider_id"])
    if "route_id" in data:
        await _ensure_route(session, data["route_id"])

    updated = await repo.update(schedule, data)
    return FlightScheduleRead.model_validate(updated, from_attributes=True)


async def delete_flight_schedule_by_id(session: AsyncSession, schedule_id: UUID) -> bool:
    repo = FlightScheduleRepository(session)
    schedule = await repo.get(schedule_id)
    if not schedule:
        return False
    await repo.delete(schedule_id)
    return True

