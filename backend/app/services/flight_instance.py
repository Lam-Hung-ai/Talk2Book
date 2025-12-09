from collections.abc import Sequence
from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.flight_instance import FlightInstance
from app.models.flight_schedule import FlightSchedule
from app.repositories.flight_instance import FlightInstanceRepository
from app.schemas.flight_instance import (
    FlightInstanceCreate,
    FlightInstanceRead,
    FlightInstanceUpdate,
)


async def _ensure_schedule(session: AsyncSession, schedule_id: UUID) -> None:
    schedule = await session.get(FlightSchedule, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Schedule {schedule_id} does not exist",
        )


def _validate_datetimes(dep, arr):
    if dep and arr and dep >= arr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dep_datetime must be earlier than arr_datetime",
        )


async def create_flight_instance(
    session: AsyncSession, payload: FlightInstanceCreate
) -> FlightInstanceRead:
    await _ensure_schedule(session, payload.schedule_id)
    _validate_datetimes(payload.dep_datetime, payload.arr_datetime)

    repo = FlightInstanceRepository(session)
    instance = await repo.create(payload)
    return FlightInstanceRead.model_validate(instance, from_attributes=True)


async def list_flight_instances(
    session: AsyncSession,
    limit: int,
    offset: int,
    schedule_id: UUID | None = None,
    flight_date: date | None = None,
    status: str | None = None,
) -> tuple[Sequence[FlightInstance], int]:
    repo = FlightInstanceRepository(session)
    items = await repo.list_filtered(
        limit=limit,
        offset=offset,
        schedule_id=schedule_id,
        flight_date=flight_date,
        status=status,
    )
    total = (await session.exec(select(FlightInstance))).all()
    return items, len(total)


async def get_flight_instance_by_id(
    session: AsyncSession, instance_id: UUID
) -> FlightInstanceRead | None:
    repo = FlightInstanceRepository(session)
    instance = await repo.get(instance_id)
    return (
        FlightInstanceRead.model_validate(instance, from_attributes=True)
        if instance
        else None
    )


async def update_flight_instance_by_id(
    session: AsyncSession, instance_id: UUID, payload: FlightInstanceUpdate
) -> FlightInstanceRead | None:
    repo = FlightInstanceRepository(session)
    instance = await repo.get(instance_id)
    if not instance:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "schedule_id" in data:
        await _ensure_schedule(session, data["schedule_id"])
    _validate_datetimes(data.get("dep_datetime", instance.dep_datetime), data.get("arr_datetime", instance.arr_datetime))

    updated = await repo.update(instance, data)
    return FlightInstanceRead.model_validate(updated, from_attributes=True)


async def delete_flight_instance_by_id(session: AsyncSession, instance_id: UUID) -> bool:
    repo = FlightInstanceRepository(session)
    instance = await repo.get(instance_id)
    if not instance:
        return False
    await repo.delete(instance_id)
    return True

