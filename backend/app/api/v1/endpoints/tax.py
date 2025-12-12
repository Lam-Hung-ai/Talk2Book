# app/api/v1/endpoints/tax.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.tax import TaxCreate, TaxRead, TaxUpdate
from app.services.tax import TaxService

router = APIRouter()


def get_tax_service(db: AsyncSession = Depends(get_async_session)) -> TaxService:
    return TaxService(db)


@router.post(
    "/",
    response_model=TaxRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo tax mới",
)
async def create_tax(
    tax_in: TaxCreate, service: TaxService = Depends(get_tax_service)
):
    """Tạo tax mới."""
    return await service.create_tax(tax_in)


@router.get("/{tax_id}", response_model=TaxRead, summary="Lấy thông tin tax theo ID")
async def get_tax(tax_id: UUID, service: TaxService = Depends(get_tax_service)):
    """Lấy thông tin tax theo ID."""
    return await service.get_tax(tax_id)


@router.get("/", response_model=dict, summary="Danh sách taxes có phân trang")
async def get_taxes(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(50, ge=1, le=100, description="Số lượng mỗi trang"),
    scope: str | None = Query(None, description="Lọc theo scope"),
    currency_code: str | None = Query(None, description="Lọc theo currency code"),
    service: TaxService = Depends(get_tax_service),
):
    """Lấy danh sách taxes với phân trang và filter."""
    return await service.get_taxes_paginated(
        page=page, page_size=page_size, scope=scope, currency_code=currency_code
    )


@router.put("/{tax_id}", response_model=TaxRead, summary="Cập nhật thông tin tax")
async def update_tax(
    tax_id: UUID, tax_in: TaxUpdate, service: TaxService = Depends(get_tax_service)
):
    """Cập nhật tax."""
    return await service.update_tax(tax_id, tax_in)


@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa tax")
async def delete_tax(tax_id: UUID, service: TaxService = Depends(get_tax_service)):
    """Xóa tax."""
    await service.delete_tax(tax_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm taxes")
async def search_taxes(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: TaxService = Depends(get_tax_service),
):
    """Tìm kiếm taxes theo name hoặc scope."""
    return await service.search_taxes(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

