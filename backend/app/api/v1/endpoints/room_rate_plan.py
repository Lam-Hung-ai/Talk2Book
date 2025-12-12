# app/api/v1/endpoints/room_rate_plan.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.room_rate_plan import (
    RoomRatePlanCreate,
    RoomRatePlanRead,
    RoomRatePlanUpdate,
)
from app.services.room_rate_plan import RoomRatePlanService

router = APIRouter()


def get_room_rate_plan_service(
    db: AsyncSession = Depends(get_async_session),
) -> RoomRatePlanService:
    return RoomRatePlanService(db)


@router.post(
    "/",
    response_model=RoomRatePlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo room rate plan mới",
)
async def create_room_rate_plan(
    rate_plan_in: RoomRatePlanCreate,
    service: RoomRatePlanService = Depends(get_room_rate_plan_service),
):
    """Endpoint tạo room rate plan mới"""
    return await service.create_room_rate_plan(rate_plan_in)


@router.get(
    "/{rate_plan_id}",
    response_model=RoomRatePlanRead,
    summary="Lấy thông tin room rate plan theo ID",
)
async def get_room_rate_plan(
    rate_plan_id: UUID,
    service: RoomRatePlanService = Depends(get_room_rate_plan_service),
):
    """Lấy thông tin room rate plan theo ID. Ném 404 nếu không tồn tại"""
    rate_plan = await service.get_room_rate_plan_by_id(rate_plan_id)
    return RoomRatePlanRead.model_validate(rate_plan, from_attributes=True)


@router.get(
    "/", response_model=dict, summary="Danh sách room rate plans có phân trang"
)
async def get_room_rate_plans(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    hotel_id: UUID | None = Query(None, description="Lọc theo hotel_id"),
    service: RoomRatePlanService = Depends(get_room_rate_plan_service),
):
    """Lấy danh sách room rate plans với phân trang và filter"""
    return await service.get_room_rate_plans_paginated(
        page=page, page_size=page_size, hotel_id=hotel_id
    )


@router.put(
    "/{rate_plan_id}",
    response_model=RoomRatePlanRead,
    summary="Cập nhật thông tin room rate plan",
)
async def update_room_rate_plan(
    rate_plan_id: UUID,
    rate_plan_in: RoomRatePlanUpdate,
    service: RoomRatePlanService = Depends(get_room_rate_plan_service),
):
    """Cập nhật room rate plan"""
    return await service.update_room_rate_plan(rate_plan_id, rate_plan_in)


@router.delete(
    "/{rate_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa room rate plan",
)
async def delete_room_rate_plan(
    rate_plan_id: UUID,
    service: RoomRatePlanService = Depends(get_room_rate_plan_service),
):
    """Xóa room rate plan"""
    await service.delete_room_rate_plan(rate_plan_id)
    return None


@router.get(
    "/search/mixin",
    response_model=dict,
    summary="Tìm kiếm room rate plans theo name hoặc meal_plan",
)
async def search_room_rate_plans(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: RoomRatePlanService = Depends(get_room_rate_plan_service),
):
    """Search room rate plans theo name và meal_plan"""
    return await service.search_room_rate_plans(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

