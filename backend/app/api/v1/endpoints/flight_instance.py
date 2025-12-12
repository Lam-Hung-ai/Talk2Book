from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.flight_instance import (
    FlightInstanceCreate,
    FlightInstanceRead,
    FlightInstanceUpdate,
)
from app.services.flight_instance import FlightInstanceService

router = APIRouter()


def get_flight_instance_service(
    db: AsyncSession = Depends(get_async_session),
) -> FlightInstanceService:
    return FlightInstanceService(db)


@router.post(
    "/",
    response_model=FlightInstanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo flight instance",
)
async def create_instance(
    payload: FlightInstanceCreate,
    service: FlightInstanceService = Depends(get_flight_instance_service),
):
    return await service.create_instance(payload)


@router.get("/", response_model=dict, summary="Danh sách flight instances")
async def list_instances(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    schedule_id: UUID | None = Query(None),
    flight_date: date | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    service: FlightInstanceService = Depends(get_flight_instance_service),
):
    return await service.list_instances(
        page=page,
        page_size=page_size,
        schedule_id=schedule_id,
        flight_date=flight_date,
        status=status_filter,
    )


@router.get(
    "/{instance_id}",
    response_model=FlightInstanceRead,
    summary="Chi tiết flight instance",
)
async def get_instance(
    instance_id: UUID, service: FlightInstanceService = Depends(get_flight_instance_service)
):
    return await service.get_instance(instance_id)


@router.put(
    "/{instance_id}",
    response_model=FlightInstanceRead,
    summary="Cập nhật flight instance",
)
async def update_instance(
    instance_id: UUID,
    payload: FlightInstanceUpdate,
    service: FlightInstanceService = Depends(get_flight_instance_service),
):
    return await service.update_instance(instance_id, payload)


@router.delete(
    "/{instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa flight instance",
)
async def delete_instance(
    instance_id: UUID, service: FlightInstanceService = Depends(get_flight_instance_service)
):
    await service.delete_instance(instance_id)
    return None

