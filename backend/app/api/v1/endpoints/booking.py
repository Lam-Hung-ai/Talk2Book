from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.schemas.booking_flow import (
    FlightBookingRequest,
    FlightBookingResult,
    HotelBookingRequest,
    HotelBookingResult,
)
from app.services.booking import BookingService

router = APIRouter()


def get_booking_service(
    db: AsyncSession = Depends(get_async_session),
) -> BookingService:
    return BookingService(db)


@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo booking",
)
async def create_booking(
    booking_in: BookingCreate, service: BookingService = Depends(get_booking_service)
):
    return await service.create_booking(booking_in)


@router.get(
    "/{booking_id}",
    response_model=BookingRead,
    summary="Lấy booking theo ID",
)
async def get_booking(
    booking_id: UUID, service: BookingService = Depends(get_booking_service)
):
    return await service.get_booking(booking_id)


@router.get("/", response_model=dict, summary="Danh sách booking có phân trang")
async def list_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: str | None = Query(None),
    state: str | None = Query(None),
    service: BookingService = Depends(get_booking_service),
):
    return await service.list_bookings(
        page=page,
        page_size=page_size,
        user_id=user_id,
        state=state,
    )


@router.put(
    "/{booking_id}",
    response_model=BookingRead,
    summary="Cập nhật booking",
)
async def update_booking(
    booking_id: UUID,
    booking_in: BookingUpdate,
    service: BookingService = Depends(get_booking_service),
):
    return await service.update_booking(booking_id, booking_in)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa booking",
)
async def delete_booking(
    booking_id: UUID, service: BookingService = Depends(get_booking_service)
):
    await service.delete_booking(booking_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm booking")
async def search_bookings(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: BookingService = Depends(get_booking_service),
):
    return await service.search_bookings(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


# ---------- FLOW: ĐẶT VÉ MÁY BAY & ĐẶT PHÒNG ----------


@router.post(
    "/flight-booking",
    response_model=FlightBookingResult,
    status_code=status.HTTP_201_CREATED,
    summary="Đặt vé máy bay (Create Booking)",
)
async def create_flight_booking(
    payload: FlightBookingRequest,
    service: BookingService = Depends(get_booking_service),
):
    """
    Tạo một đơn đặt vé mới (Booking) dựa trên chuyến bay đã chọn.

    Hàm này nhận thông tin từ kết quả tìm kiếm (`instance_id`, `cabin`...) và
    tạo ra booking ở trạng thái chờ thanh toán (`pending_payment`). Nó cũng tạm thời
    giữ chỗ (reserve seats) và sinh mã vé.

    **Lưu ý quan trọng cho AI Agent:**
    - Cần gọi tool `search_flights` trước để lấy `instance_id` hợp lệ.
    - `user_id` phải là ID của người dùng đang chat hiện tại.

    Request Body Schema:
        {
            "user_id": UUID,        # ID người dùng (VD: "3e7dbe94...")
            "instance_id": UUID,    # ID chuyến bay từ bước search (VD: "de60971e...")
            "cabin": str,           # Hạng ghế (VD: "economy")
            "passengers": int,      # Số khách (VD: 1)
            "currency_code": str    # Tiền tệ (VD: "VND")
        }

    Response Schema:
        {
            "booking": {
                "id": UUID,             # Mã đơn hàng hệ thống
                "state": str,           # Trạng thái (quan trọng: "pending_payment")
                "total_amount": str,    # Tổng tiền cần thanh toán
                ...
            },
            "item": { ... },            # Chi tiết sản phẩm đã mua
            "tickets": [                # Danh sách vé được xuất
                {
                    "code": str,        # Mã vé (dùng để check-in)
                    ...
                }
            ]
        }

    Example Response:
        {
            "booking": {
                "user_id": "3e7dbe94-a397-4a4d-9c40-7dd3af793c9b",
                "state": "pending_payment",
                "currency_code": "VND",
                "total_amount": "2595000.00",
                "id": "e89b13f6-2833-4f18-b979-75826f1f9cf6",
                "created_at": "2025-12-17T13:30:39.399324Z",
                "updated_at": "2025-12-17T13:30:39.399390Z"
            },
            "item": {
                "booking_id": "e89b13f6-2833-4f18-b979-75826f1f9cf6",
                "vertical": "flight",
                "supplier_ref": "de60971e-4255-49c4-85e1-1c30b31ea796",
                "details": {
                    "type": "flight",
                    "cabin": "economy",
                    "route": {
                        "origin": "HAN",
                        "destination": "SGN",
                        "distance_km": 1730
                    },
                    "passengers": 1,
                    "flight_date": "2025-12-20",
                    "arr_datetime": "2025-12-20T01:15:00+00:00",
                    "dep_datetime": "2025-12-19T23:00:00+00:00",
                    "flight_number": "VN201",
                    "base_price_per_pax": "2595000"
                },
                "price_amount": "2595000.00",
                "id": "76596ef3-00f6-478c-a054-f83c55ea2623"
            },
            "tickets": [
                {
                    "item_id": "76596ef3-00f6-478c-a054-f83c55ea2623",
                    "type": "flight",
                    "code": "VN201-20251220-e89b13-1",
                    "id": "d521fb2d-785f-49ae-b093-575c2b300dd5",
                    "issued_at": "2025-12-17T13:30:39.406452Z"
                }
            ]
        }
    """

    return await service.create_flight_booking(payload)


@router.post(
    "/hotel-booking",
    response_model=HotelBookingResult,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo đơn đặt phòng khách sạn (Create Booking)",
)
async def create_hotel_booking(
    payload: HotelBookingRequest,
    service: BookingService = Depends(get_booking_service),
):
    """
    Tạo booking khách sạn chính thức dựa trên các lựa chọn trước đó.

    Hàm này sẽ khóa phòng (reserve inventory), tạo đơn hàng ở trạng thái `pending_payment`
    và trả về mã đơn hàng để tiến hành thanh toán.

    **Quy tắc bắt buộc cho AI Agent:**
    1. **Context Check:** Phải lấy `room_id` và `rate_plan_id` chính xác từ kết quả của tool `get_hotel_availability`.
       Tuyệt đối không tự bịa ID.
    2. **Consistency:** `check_in`, `check_out`, `guests` phải khớp với thông tin user đã tìm kiếm trước đó.
    3. **Confirmation:** Sau khi gọi tool này thành công, hãy dùng thông tin trong `item.details` (như `hotel_name`, `rate_plan_name`, `total_amount`) để xác nhận lại với người dùng.

    Request Body Schema:
        {
            "user_id": UUID,
            "hotel_id": UUID,       # ID Khách sạn
            "room_id": UUID,        # ID Loại phòng
            "rate_plan_id": UUID,   # ID Gói giá (VD: Gói bao gồm ăn sáng)
            "check_in": "YYYY-MM-DD",
            "check_out": "YYYY-MM-DD",
            "rooms": int,
            "guests": int,
            "currency_code": "VND"
        }

    Response Schema:
        {
            "booking": {
                "id": UUID,             # Mã booking hệ thống
                "state": "pending_payment",
                "total_amount": str,    # Tổng tiền phải trả
                ...
            },
            "item": {
                "details": {
                    "hotel_name": str,      # Tên khách sạn
                    "room_code": str,       # Mã phòng (STD/DLX)
                    "rate_plan_name": str,  # Tên gói (VD: Giá cơ bản)
                    "nights": int           # Số đêm
                    ...
                }
            }
        }

    Example Response:
        {
            "booking": {
                "user_id": "3e7dbe94-a397-4a4d-9c40-7dd3af793c9b",
                "state": "pending_payment",
                "currency_code": "VND",
                "total_amount": "5662000.00",
                "id": "ce138c42-3c16-4efa-983a-258b73c4c004",
                "created_at": "2025-12-17T13:43:21.239995Z",
                "updated_at": "2025-12-17T13:43:21.240006Z"
            },
            "item": {
                "booking_id": "ce138c42-3c16-4efa-983a-258b73c4c004",
                "vertical": "hotel",
                "supplier_ref": "aafca8d6-a238-4d39-8f0e-80ec3b458a85",
                "details": {
                    "type": "hotel",
                    "rooms": 1,
                    "guests": 1,
                    "nights": 2,
                    "room_id": "d863a447-8646-47ad-b4f6-16194df19928",
                    "check_in": "2025-12-20",
                    "hotel_id": "aafca8d6-a238-4d39-8f0e-80ec3b458a85",
                    "check_out": "2025-12-22",
                    "room_code": "STD",
                    "hotel_name": "Vinpearl Hotel Times City",
                    "rate_plan_id": "8b1a5e46-7085-4aff-988f-3fbfb98b8127",
                    "currency_code": "VND",
                    "rate_plan_name": "Giá cơ bản"
                },
                "price_amount": "5662000.00",
                "id": "9e07d04e-84ab-475d-8029-4e91eb0d9e12"
            }
        }
    """

    return await service.create_hotel_booking(payload)
