# app/api/v1/endpoints/search.py
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models.enums import CabinType, FareBucketType
from app.schemas.search import (
    FlightSearchRequest,
    FlightSearchResponse,
    HotelAvailabilityRequest,
    HotelAvailabilityResponse,
    HotelSearchRequest,
    HotelSearchResponse,
)
from app.services.search import SearchService

router = APIRouter()


def get_search_service(db: AsyncSession = Depends(get_async_session)) -> SearchService:
    return SearchService(db)


@router.get(
    "/flights",
    response_model=FlightSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm chuyến bay",
    description="""
    Tìm chuyến bay theo origin, destination và ngày bay.
    Backend sẽ join Route -> Schedule -> Instance và check SeatInventory để chỉ trả về các chuyến bay còn ghế.

    - **origin**: IATA code của sân bay đi (3 ký tự)
    - **destination**: IATA code của sân bay đến (3 ký tự)
    - **flight_date**: Ngày bay
    - **cabin**: (Optional) Loại cabin để filter
    - **fare_bucket**: (Optional) Fare bucket để filter
    """,
)
async def search_flights(
    origin: str = Query(..., min_length=3, max_length=3, description="IATA code sân bay đi"),
    destination: str = Query(..., min_length=3, max_length=3, description="IATA code sân bay đến"),
    flight_date: str = Query(..., description="Ngày bay (YYYY-MM-DD)"),
    cabin: CabinType | None = Query(None, description="Loại cabin (economy/premium/business/first)"),
    fare_bucket: FareBucketType | None = Query(None, description="Fare bucket"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    service: SearchService = Depends(get_search_service),
):
    """Tìm chuyến bay với logic phức tạp: join và check seat inventory"""

    # Parse date
    try:
        flight_date_parsed = datetime.strptime(flight_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD",
        )

    cabin_enum = None
    if cabin:
        try:
            cabin_enum = CabinType(cabin)
        except ValueError:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Loại cabin không hợp lệ: {cabin}",
            )

    fare_bucket_enum = None
    if fare_bucket:
        try:
            fare_bucket_enum = FareBucketType(fare_bucket)
        except ValueError:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fare bucket không hợp lệ: {fare_bucket}",
            )

    request = FlightSearchRequest(
        origin=origin.upper(),
        destination=destination.upper(),
        flight_date=flight_date_parsed,
        cabin=cabin_enum,
        fare_bucket=fare_bucket_enum,
    )

    return await service.search_flights(request, page=page, page_size=page_size)


@router.get(
    "/hotels",
    response_model=HotelSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm khách sạn",
    description="""
    Tìm khách sạn theo thành phố, ngày check-in/check-out và số khách.
    Backend sẽ quét RoomInventoryDaily trong khoảng ngày để tìm các khách sạn có phòng còn trống liên tiếp.
    
    - **city_id**: ID của thành phố
    - **check_in**: Ngày check-in (YYYY-MM-DD)
    - **check_out**: Ngày check-out (YYYY-MM-DD)
    - **guests**: Số lượng khách
    - **rooms**: Số lượng phòng cần đặt (mặc định: 1)
    """,
)
async def search_hotels(
    city_id: UUID = Query(..., description="ID của thành phố"),
    check_in: str = Query(..., description="Ngày check-in (YYYY-MM-DD)"),
    check_out: str = Query(..., description="Ngày check-out (YYYY-MM-DD)"),
    guests: int = Query(..., ge=1, description="Số lượng khách"),
    rooms: int = Query(1, ge=1, description="Số lượng phòng cần đặt"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    service: SearchService = Depends(get_search_service),
):
    """Tìm khách sạn với logic phức tạp: check room availability trong khoảng ngày"""
    # Parse dates
    try:
        check_in_parsed = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_parsed = datetime.strptime(check_out, "%Y-%m-%d").date()
    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD",
        )

    request = HotelSearchRequest(
        city_id=city_id,
        check_in=check_in_parsed,
        check_out=check_out_parsed,
        guests=guests,
        rooms=rooms,
    )

    return await service.search_hotels(request, page=page, page_size=page_size)


@router.get(
    "/hotels/{hotel_id}/availability",
    response_model=HotelAvailabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Chi tiết phòng & Giá của khách sạn",
    description="""
    Khi user bấm vào khách sạn, cần list các loại phòng (Room) + Giá tổng (base_price * số đêm) 
    cho khoảng ngày đã chọn.
    
    - **hotel_id**: ID của khách sạn
    - **check_in**: Ngày check-in (YYYY-MM-DD)
    - **check_out**: Ngày check-out (YYYY-MM-DD)
    """,
)
async def get_hotel_availability(
    hotel_id: UUID,
    check_in: str = Query(..., description="Ngày check-in (YYYY-MM-DD)"),
    check_out: str = Query(..., description="Ngày check-out (YYYY-MM-DD)"),
    service: SearchService = Depends(get_search_service),
):
    """Lấy chi tiết phòng và giá của khách sạn cho khoảng ngày"""
    from datetime import datetime

    # Parse dates
    try:
        check_in_parsed = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_parsed = datetime.strptime(check_out, "%Y-%m-%d").date()
    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD",
        )

    request = HotelAvailabilityRequest(
        check_in=check_in_parsed,
        check_out=check_out_parsed,
    )

    return await service.get_hotel_availability(hotel_id, request)

