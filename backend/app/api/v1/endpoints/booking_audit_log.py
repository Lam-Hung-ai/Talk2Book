from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.booking_audit_log import (
    BookingAuditLogCreate,
    BookingAuditLogRead,
    BookingAuditLogUpdate,
)
from app.services.booking_audit_log import BookingAuditLogService

router = APIRouter()


def get_booking_audit_log_service(
    db: AsyncSession = Depends(get_async_session),
) -> BookingAuditLogService:
    return BookingAuditLogService(db)


@router.post(
    "/",
    response_model=BookingAuditLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo booking audit log",
)
async def create_booking_audit_log(
    log_in: BookingAuditLogCreate,
    service: BookingAuditLogService = Depends(get_booking_audit_log_service),
):
    return await service.create_log(log_in)


@router.get(
    "/{log_id}",
    response_model=BookingAuditLogRead,
    summary="Lấy booking audit log theo ID",
)
async def get_booking_audit_log(
    log_id: UUID,
    service: BookingAuditLogService = Depends(get_booking_audit_log_service),
):
    return await service.get_log(log_id)


@router.get("/", response_model=dict, summary="Danh sách booking audit log")
async def list_booking_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    booking_id: UUID | None = Query(None),
    service: BookingAuditLogService = Depends(get_booking_audit_log_service),
):
    return await service.list_logs(
        page=page,
        page_size=page_size,
        booking_id=booking_id,
    )


@router.put(
    "/{log_id}",
    response_model=BookingAuditLogRead,
    summary="Cập nhật booking audit log",
)
async def update_booking_audit_log(
    log_id: UUID,
    log_in: BookingAuditLogUpdate,
    service: BookingAuditLogService = Depends(get_booking_audit_log_service),
):
    return await service.update_log(log_id, log_in)


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa booking audit log",
)
async def delete_booking_audit_log(
    log_id: UUID,
    service: BookingAuditLogService = Depends(get_booking_audit_log_service),
):
    await service.delete_log(log_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm booking audit log")
async def search_booking_audit_logs(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: BookingAuditLogService = Depends(get_booking_audit_log_service),
):
    return await service.search_logs(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
