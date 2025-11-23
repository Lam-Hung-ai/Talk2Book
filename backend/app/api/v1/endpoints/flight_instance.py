from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.flight_instance import (
    FlightInstanceCreate,
    FlightInstanceRead,
    FlightInstanceUpdate,
)
from app.services.flight_instance import (
    create_flight_instance,
    delete_flight_instance_by_id,
    get_flight_instance_by_id,
    list_flight_instances,
    update_flight_instance_by_id,
)

router = APIRouter()


@router.post(
    "",
    response_model=FlightInstanceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_flight_instance_ep(
    payload: FlightInstanceCreate,
    session: AsyncSession = Depends(get_async_session),
):
    instance = await create_flight_instance(session, payload)
    return instance


@router.get(
    "/",
    response_model=list[FlightInstanceRead],
)
async def list_flight_instances_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    schedule_id: UUID | None = Query(None),
    flight_date: date | None = Query(None),
    status: str | None = Query(None, description="Filter by flight status"),
):
    items, _ = await list_flight_instances(
        session=session,
        limit=limit,
        offset=offset,
        schedule_id=schedule_id,
        flight_date=flight_date,
        status=status,
    )
    return items


@router.get(
    "/{instance_id}",
    response_model=FlightInstanceRead,
)
async def get_flight_instance_ep(
    instance_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    instance = await get_flight_instance_by_id(session, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Flight instance not found")
    return instance


@router.put(
    "/{instance_id}",
    response_model=FlightInstanceRead,
)
async def update_flight_instance_ep(
    instance_id: UUID,
    payload: FlightInstanceUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    instance = await update_flight_instance_by_id(session, instance_id, payload)
    if not instance:
        raise HTTPException(status_code=404, detail="Flight instance not found")
    return instance


@router.delete(
    "/{instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_flight_instance_ep(
    instance_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_flight_instance_by_id(session, instance_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Flight instance not found")
    return None
