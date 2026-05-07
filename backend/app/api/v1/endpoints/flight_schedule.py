from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.flight_schedule import (
    FlightScheduleCreate,
    FlightScheduleRead,
    FlightScheduleUpdate,
)
from app.services.flight_schedule import FlightScheduleService

router = APIRouter()


def get_flight_schedule_service(
    db: AsyncSession = Depends(get_async_session),
) -> FlightScheduleService:
    return FlightScheduleService(db)


@router.post(
    "/",
    response_model=FlightScheduleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo flight schedule",
)
async def create_schedule(
    payload: FlightScheduleCreate,
    service: FlightScheduleService = Depends(get_flight_schedule_service),
):
    return await service.create_schedule(payload)


@router.get("/", response_model=dict, summary="Danh sách flight schedules")
async def list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    q: str | None = Query(None, description="Tìm theo flight_number"),
    provider_id: UUID | None = Query(None),
    route_id: UUID | None = Query(None),
    dow: int | None = Query(None, description="Bitstring as int, e.g. 1000000"),
    service: FlightScheduleService = Depends(get_flight_schedule_service),
):
    return await service.list_schedules(
        page=page,
        page_size=page_size,
        q=q,
        provider_id=provider_id,
        route_id=route_id,
        dow=dow,
    )


@router.get(
    "/{schedule_id}",
    response_model=FlightScheduleRead,
    summary="Chi tiết flight schedule",
)
async def get_schedule(
    schedule_id: UUID,
    service: FlightScheduleService = Depends(get_flight_schedule_service),
):
    return await service.get_schedule(schedule_id)


@router.put(
    "/{schedule_id}",
    response_model=FlightScheduleRead,
    summary="Cập nhật flight schedule",
)
async def update_schedule(
    schedule_id: UUID,
    payload: FlightScheduleUpdate,
    service: FlightScheduleService = Depends(get_flight_schedule_service),
):
    return await service.update_schedule(schedule_id, payload)


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa flight schedule",
)
async def delete_schedule(
    schedule_id: UUID,
    service: FlightScheduleService = Depends(get_flight_schedule_service),
):
    await service.delete_schedule(schedule_id)
    return None
