# app/api/v1/endpoints/price_quote.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.price_quote import PriceQuoteCreate, PriceQuoteRead, PriceQuoteUpdate
from app.services.price_quote import PriceQuoteService

router = APIRouter()


def get_price_quote_service(
    db: AsyncSession = Depends(get_async_session),
) -> PriceQuoteService:
    return PriceQuoteService(db)


@router.post(
    "/",
    response_model=PriceQuoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo price quote mới",
)
async def create_price_quote(
    quote_in: PriceQuoteCreate,
    service: PriceQuoteService = Depends(get_price_quote_service),
):
    """Tạo price quote mới."""
    return await service.create_price_quote(quote_in)


@router.get(
    "/{quote_id}",
    response_model=PriceQuoteRead,
    summary="Lấy thông tin price quote theo ID",
)
async def get_price_quote(
    quote_id: UUID, service: PriceQuoteService = Depends(get_price_quote_service)
):
    """Lấy thông tin price quote theo ID."""
    return await service.get_price_quote(quote_id)


@router.get("/", response_model=dict, summary="Danh sách price quotes có phân trang")
async def get_price_quotes(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(50, ge=1, le=100, description="Số lượng mỗi trang"),
    user_id: str | None = Query(None, description="Lọc theo user ID"),
    vertical: str | None = Query(None, description="Lọc theo vertical"),
    currency_code: str | None = Query(None, description="Lọc theo currency code"),
    service: PriceQuoteService = Depends(get_price_quote_service),
):
    """Lấy danh sách price quotes với phân trang và filter."""
    return await service.get_price_quotes_paginated(
        page=page,
        page_size=page_size,
        user_id=user_id,
        vertical=vertical,
        currency_code=currency_code,
    )


@router.put(
    "/{quote_id}",
    response_model=PriceQuoteRead,
    summary="Cập nhật thông tin price quote",
)
async def update_price_quote(
    quote_id: UUID,
    quote_in: PriceQuoteUpdate,
    service: PriceQuoteService = Depends(get_price_quote_service),
):
    """Cập nhật price quote."""
    return await service.update_price_quote(quote_id, quote_in)


@router.delete(
    "/{quote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa price quote",
)
async def delete_price_quote(
    quote_id: UUID, service: PriceQuoteService = Depends(get_price_quote_service)
):
    """Xóa price quote."""
    await service.delete_price_quote(quote_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm price quotes")
async def search_price_quotes(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: PriceQuoteService = Depends(get_price_quote_service),
):
    """Tìm kiếm price quotes theo vertical."""
    return await service.search_price_quotes(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
