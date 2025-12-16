# app/api/v1/endpoints/exchange_rate.py
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.exchange_rate import (
    ExchangeRateCreate,
    ExchangeRateRead,
    ExchangeRateUpdate,
)
from app.services.exchange_rate import ExchangeRateService

router = APIRouter()


def get_exchange_rate_service(
    db: AsyncSession = Depends(get_async_session),
) -> ExchangeRateService:
    return ExchangeRateService(db)


@router.post(
    "/",
    response_model=ExchangeRateRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo exchange rate mới",
)
async def create_exchange_rate(
    rate_in: ExchangeRateCreate,
    service: ExchangeRateService = Depends(get_exchange_rate_service),
):
    """Tạo exchange rate mới."""
    return await service.create_exchange_rate(rate_in)


@router.get(
    "/{rate_date}/{base}/{quote}",
    response_model=ExchangeRateRead,
    summary="Lấy thông tin exchange rate",
)
async def get_exchange_rate(
    rate_date: date,
    base: str,
    quote: str,
    service: ExchangeRateService = Depends(get_exchange_rate_service),
):
    """Lấy thông tin exchange rate theo ngày và cặp tiền tệ."""
    return await service.get_exchange_rate(rate_date, base, quote)


@router.get("/", response_model=dict, summary="Danh sách exchange rates có phân trang")
async def get_exchange_rates(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(50, ge=1, le=100, description="Số lượng mỗi trang"),
    rate_date: date | None = Query(None, description="Lọc theo ngày"),
    base: str | None = Query(None, description="Lọc theo base currency"),
    quote: str | None = Query(None, description="Lọc theo quote currency"),
    service: ExchangeRateService = Depends(get_exchange_rate_service),
):
    """Lấy danh sách exchange rates với phân trang và filter."""
    return await service.get_exchange_rates_paginated(
        page=page,
        page_size=page_size,
        rate_date=rate_date,
        base=base,
        quote=quote,
    )


@router.put(
    "/{rate_date}/{base}/{quote}",
    response_model=ExchangeRateRead,
    summary="Cập nhật thông tin exchange rate",
)
async def update_exchange_rate(
    rate_date: date,
    base: str,
    quote: str,
    rate_in: ExchangeRateUpdate,
    service: ExchangeRateService = Depends(get_exchange_rate_service),
):
    """Cập nhật exchange rate."""
    return await service.update_exchange_rate(rate_date, base, quote, rate_in)


@router.delete(
    "/{rate_date}/{base}/{quote}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa exchange rate",
)
async def delete_exchange_rate(
    rate_date: date,
    base: str,
    quote: str,
    service: ExchangeRateService = Depends(get_exchange_rate_service),
):
    """Xóa exchange rate."""
    await service.delete_exchange_rate(rate_date, base, quote)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm exchange rates"
)
async def search_exchange_rates(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: ExchangeRateService = Depends(get_exchange_rate_service),
):
    """Tìm kiếm exchange rates theo base hoặc quote."""
    return await service.search_exchange_rates(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

