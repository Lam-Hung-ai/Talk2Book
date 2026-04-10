# app/api/v1/endpoints/search.py
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models.enums import CabinType
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
    """,
)
async def search_flights(
    origin: str = Query(..., min_length=3, max_length=3, description="Mã IATA sân bay đi (VD: HAN)"),
    destination: str = Query(..., min_length=3, max_length=3, description="Mã IATA sân bay đến (VD: SGN)"),
    flight_date: str = Query(..., description="Ngày bay định dạng YYYY-MM-DD"),
    cabin: CabinType | None = Query(None, description="Hạng ghế: economy, premium, business, first"),
    page: int = Query(1, ge=1, description="Số trang kết quả"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng kết quả mỗi trang"),
    service: SearchService = Depends(get_search_service),
):
    """
    Tìm kiếm các chuyến bay khả dụng dựa trên hành trình và ngày khởi hành.

    Hệ thống sẽ thực hiện query phức tạp: Join Route -> Schedule -> Instance và kiểm tra
    SeatInventory để đảm bảo **chỉ trả về các chuyến bay còn ghế trống**.

    Args:
        origin (str): Mã sân bay đi (IATA 3 ký tự). Ví dụ: "HAN", "SGN".
        destination (str): Mã sân bay đến (IATA 3 ký tự). Ví dụ: "DAD", "CXR".
        flight_date (str): Ngày bay mong muốn, bắt buộc theo định dạng "YYYY-MM-DD".
                           Ví dụ: "2025-12-20".
        cabin (str, optional): Lọc theo hạng ghế. Các giá trị: "economy", "premium", "business", "first".
        page (int): Trang hiện tại (mặc định: 1).
        page_size (int): Số lượng bản ghi/trang (mặc định: 20).

    Returns:
        dict: Danh sách các chuyến bay thỏa mãn điều kiện và còn chỗ.

    Response Schema:
        {
            "items": [
                {
                    "instance_id": UUID,       # ID định danh của chuyến bay cụ thể
                    "flight_number": str,      # Số hiệu chuyến bay (VD: "VN201")
                    "provider_name": str,      # Hãng hàng không (VD: "Vietnam Airlines")
                    "origin": str,             # Sân bay đi (VD: "HAN")
                    "destination": str,        # Sân bay đến (VD: "SGN")
                    "dep_datetime": datetime,  # Thời gian khởi hành (ISO 8601)
                    "arr_datetime": datetime,  # Thời gian hạ cánh (ISO 8601)
                    "flight_date": date,       # Ngày bay thực tế
                    "status": str,             # Trạng thái (VD: "scheduled")
                    "available_seats": int,    # Số ghế còn trống thực tế
                    "cabin": str,              # Hạng ghế
                    "total_seats": int,        # Tổng số ghế thiết kế
                    "sold_seats": int          # Số ghế đã bán
                }
            ],
            "total": int,
            "page": int,
            "page_size": int,
            "total_pages": int
        }

    Example Response:
        {
            "items": [
                {
                    "instance_id": "de60971e-4255-49c4-85e1-1c30b31ea796",
                    "flight_number": "VN201",
                    "provider_name": "Vietnam Airlines",
                    "origin": "HAN",
                    "destination": "SGN",
                    "dep_datetime": "2025-12-19T23:00:00Z",
                    "arr_datetime": "2025-12-20T01:15:00Z",
                    "flight_date": "2025-12-20",
                    "status": "scheduled",
                    "available_seats": 10,
                    "cabin": "economy",
                    "total_seats": 25,
                    "sold_seats": 12
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
        }
    """

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

    request = FlightSearchRequest(
        origin=origin.upper(),
        destination=destination.upper(),
        flight_date=flight_date_parsed,
        cabin=cabin_enum,
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
    city_id: UUID = Query(..., description="ID thành phố (Lấy từ API get_cities)"),
    check_in: str = Query(..., description="Ngày nhận phòng (YYYY-MM-DD)"),
    check_out: str = Query(..., description="Ngày trả phòng (YYYY-MM-DD)"),
    guests: int = Query(..., ge=1, description="Tổng số khách"),
    rooms: int = Query(1, ge=1, description="Số lượng phòng cần đặt"),
    page: int = Query(1, ge=1, description="Số trang kết quả"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng kết quả mỗi trang"),
    service: SearchService = Depends(get_search_service),
):
    """
    Tìm kiếm khách sạn khả dụng tại một thành phố trong khoảng thời gian cụ thể.

    Hệ thống sẽ quét kho phòng (Inventory) để tìm các khách sạn có phòng trống
    **liên tiếp** từ ngày check-in đến check-out.

    **Hướng dẫn cho AI Agent:**
    1. Bắt buộc phải gọi tool `get_cities` trước để lấy `city_id` chính xác (UUID).
       Không được tự đoán `city_id` hoặc gửi tên thành phố dạng string.
    2. Ngày `check_out` phải lớn hơn `check_in`.
    3. `min_price` trả về là giá tham khảo thấp nhất, giá thực tế sẽ có ở bước chọn phòng chi tiết.

    Args:
        city_id (UUID): ID định danh của thành phố (VD: "d2063e38...").
        check_in (str): Ngày nhận phòng, định dạng "YYYY-MM-DD".
        check_out (str): Ngày trả phòng, định dạng "YYYY-MM-DD".
        guests (int): Tổng số người lớn và trẻ em.
        rooms (int): Số lượng phòng muốn đặt (mặc định là 1).

    Returns:
        dict: Danh sách khách sạn kèm thông tin giá và vị trí.

    Response Schema:
        {
            "items": [
                {
                    "hotel_id": UUID,
                    "hotel_name": str,
                    "provider_name": str,  # VD: "Vinpearl", "InterContinental"
                    "star_rating": str,    # VD: "5.0"
                    "address": str,
                    "lat": str,            # Hữu ích để hiển thị bản đồ
                    "lng": str,
                    "available_rooms": int,# Số phòng thực tế còn lại
                    "min_price": str,      # Giá sàn (VD: "5482000.00")
                    "currency_code": str
                }
            ],
            "total": int,
            "page": int,
            "page_size": int,
            "total_pages": int
        }

    Example Response:
        {
            "items": [
                {
                    "hotel_id": "aafca8d6-a238-4d39-8f0e-80ec3b458a85",
                    "hotel_name": "Vinpearl Hotel Times City",
                    "provider_name": "Vinpearl Hotels & Resorts",
                    "city_name": "Hà Nội",
                    "star_rating": "5.0",
                    "address": "458 Minh Khai, Hai Bà Trưng, Hà Nội",
                    "lat": "20.998400",
                    "lng": "105.862100",
                    "available_rooms": 6,
                    "min_price": "5482000.00",
                    "currency_code": "VND"
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
        }
    """
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
    hotel_id: UUID = Path(..., description="ID khách sạn (Lấy từ kết quả search_hotels)"),
    check_in: str = Query(..., description="Ngày check-in (YYYY-MM-DD)"),
    check_out: str = Query(..., description="Ngày check-out (YYYY-MM-DD)"),
    service: SearchService = Depends(get_search_service),
):
    """
    Lấy danh sách các loại phòng và gói giá (Rate Plan) khả dụng của một khách sạn cụ thể.

    API này trả về chi tiết từng option có thể đặt (bookable options).
    Lưu ý: Cùng một loại phòng (VD: Standard) có thể xuất hiện nhiều lần với các gói giá khác nhau 
    (VD: Giá cơ bản vs Giá bao gồm ăn sáng).

    **Hướng dẫn cho AI Agent:**
    1. Dùng `hotel_id` mà người dùng đã chọn từ bước `Google Hotels`.
    2. Giữ nguyên `check_in` và `check_out` như lúc search để đảm bảo giá chính xác.
    3. Giải thích cho người dùng sự khác biệt giữa các option dựa trên `meal_plan`:
       - **RO (Room Only)**: Không bao gồm ăn sáng.
       - **BB (Bed & Breakfast)**: Bao gồm ăn sáng.
    4. Khi người dùng chốt đơn, hãy ghi nhớ cặp `room_id` và `rate_plan_id` để gọi API booking.

    Args:
        hotel_id (UUID): ID của khách sạn.
        check_in (str): Ngày nhận phòng (YYYY-MM-DD).
        check_out (str): Ngày trả phòng (YYYY-MM-DD).

    Returns:
        dict: Danh sách các phòng kèm giá chi tiết.

    Response Schema:
        {
            "hotel_id": UUID,
            "hotel_name": str,
            "nights": int,      # Tổng số đêm lưu trú
            "rooms": [
                {
                    "room_id": UUID,        # ID phòng
                    "room_code": str,       # Mã phòng (STD, SUITE...)
                    "bed_config": str,      # Mô tả giường
                    "rate_plan_id": UUID,   # ID gói giá (QUAN TRỌNG ĐỂ BOOKING)
                    "rate_plan_name": str,  # Tên hiển thị gói giá
                    "meal_plan": str,       # RO=Không ăn, BB=Ăn sáng
                    "total_price": str,     # Tổng tiền
                    "price_per_night": str, # Giá/đêm
                    "available_rooms": int  # Số lượng còn lại
                }
            ]
        }

    Example Response:
        {
            "hotel_id": "aafca8d6-a238-4d39-8f0e-80ec3b458a85",
            "hotel_name": "Vinpearl Hotel Times City",
            "check_in": "2025-12-20",
            "check_out": "2025-12-22",
            "nights": 2,
            "rooms": [
                {
                    "room_id": "d863a447-8646-47ad-b4f6-16194df19928",
                    "room_code": "STD",
                    "bed_config": "1 giường đôi",
                    "rate_plan_id": "70433f36-9caf-4b9c-9d71-330eae958e4c",
                    "rate_plan_name": "Bao gồm bữa sáng",
                    "meal_plan": "BB",
                    "total_price": "5482000.00",
                    "price_per_night": "2741000.00",
                    "available_rooms": 1,
                    "currency_code": "VND"
                }
            ]
        }
    """
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

