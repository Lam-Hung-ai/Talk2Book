from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.booking import Booking
from app.models.booking_item import BookingItem
from app.models.enums import BookingState, TicketType
from app.models.flight_instance import FlightInstance
from app.models.flight_schedule import FlightSchedule
from app.models.hotel import Hotel
from app.models.hotel_room import HotelRoom
from app.models.room_inventory_daily import RoomInventoryDaily
from app.models.room_rate_plan import RoomRatePlan
from app.models.route import Route
from app.models.seat_inventory import SeatInventory
from app.models.ticket import Ticket
from app.repositories.booking import BookingRepository
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.schemas.booking_flow import (
    FlightBookingRequest,
    FlightBookingResult,
    HotelBookingRequest,
    HotelBookingResult,
)
from app.schemas.booking_item import BookingItemRead
from app.schemas.ticket import TicketRead


class BookingService:
    def __init__(self, db: AsyncSession):
        self.repo = BookingRepository(db)
        self.db = db

    async def create_booking(self, booking_in: BookingCreate) -> BookingRead:
        booking = await self.repo.create(booking_in)
        return BookingRead.model_validate(booking, from_attributes=True)

    async def get_booking(self, booking_id: UUID) -> BookingRead:
        booking = await self.repo.get_or_404(booking_id, detail="Booking not found")
        return BookingRead.model_validate(booking, from_attributes=True)

    async def list_bookings(
        self,
        page: int = 1,
        page_size: int = 50,
        user_id: UUID | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if user_id is not None:
            filters["user_id"] = user_id
        if state is not None:
            filters["state"] = state

        bookings = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [BookingRead.model_validate(b, from_attributes=True) for b in bookings],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_booking(self, booking_id: UUID, booking_in: BookingUpdate) -> BookingRead:
        booking = await self.repo.get_or_404(booking_id, detail="Booking not found")
        updated = await self.repo.update(booking, booking_in)
        return BookingRead.model_validate(updated, from_attributes=True)

    async def delete_booking(self, booking_id: UUID) -> None:
        await self.repo.delete(booking_id)

    async def search_bookings(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        bookings = await self.repo.search(
            query=q,
            search_columns=["state"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["state"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [BookingRead.model_validate(b, from_attributes=True) for b in bookings],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    # ---------- FLOW: ĐẶT VÉ MÁY BAY ----------

    async def create_flight_booking(
        self, payload: FlightBookingRequest
    ) -> FlightBookingResult:
        """
        Đặt vé máy bay dựa trên FlightInstance + SeatInventory.
        - Tạo Booking + BookingItem
        - (Optional) Tạo Ticket placeholder cho từng hành khách
        """

        # Lấy instance + schedule + route
        stmt = (
            select(FlightInstance, FlightSchedule, Route)
            .join(FlightSchedule, FlightInstance.schedule_id == FlightSchedule.id)  # type: ignore[arg-type]
            .join(Route, FlightSchedule.route_id == Route.id)  # type: ignore[arg-type]
            .where(FlightInstance.id == payload.instance_id)
        )
        res = await self.db.exec(stmt)
        row = res.first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy chuyến bay (instance) tương ứng",
            )
        instance, schedule, route = row

        # Lấy seat inventory cho cabin + fare_bucket
        seat_stmt = select(SeatInventory).where(
            SeatInventory.instance_id == instance.id,
            SeatInventory.cabin == payload.cabin,
            SeatInventory.fare_bucket == payload.fare_bucket,
        )
        seat_res = await self.db.exec(seat_stmt)
        seat = seat_res.first()
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy seat inventory phù hợp để đặt chỗ",
            )

        available = seat.total_seats - seat.sold_seats - seat.held_seats
        if available < payload.passengers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không đủ ghế trống cho số lượng hành khách yêu cầu",
            )

        # Tính giá vé đơn giản dựa trên distance_km của route
        distance = route.distance_km or 500
        base_price_per_pax = Decimal(distance) * Decimal("1500")  # 500km ~ 750k

        total_amount = base_price_per_pax * payload.passengers

        # Tạo Booking
        booking = Booking(
            user_id=payload.user_id,
            state=BookingState.pending_payment,
            currency_code=payload.currency_code,
            total_amount=total_amount,
            quote_id=None,
            coupon_id=None,
        )
        self.db.add(booking)
        await self.db.flush()  # lấy booking.id

        # Tạo BookingItem
        details: dict[str, Any] = {
            "type": "flight",
            "flight_number": schedule.flight_number,
            "route": {
                "origin": route.origin,
                "destination": route.destination,
                "distance_km": route.distance_km,
            },
            "flight_date": instance.flight_date.isoformat(),
            "dep_datetime": instance.dep_datetime.isoformat(),
            "arr_datetime": instance.arr_datetime.isoformat(),
            "cabin": payload.cabin,
            "fare_bucket": payload.fare_bucket,
            "passengers": payload.passengers,
            "base_price_per_pax": str(base_price_per_pax),
        }

        item = BookingItem(
            booking_id=booking.id,
            vertical="flight",
            supplier_ref=str(instance.id),
            details=details,
            price_amount=total_amount,
        )
        self.db.add(item)

        # (Optional) tạo ticket placeholder cho từng hành khách
        tickets: list[Ticket] = []
        for idx in range(payload.passengers):
            code = f"{schedule.flight_number}-{instance.flight_date.strftime('%Y%m%d')}-{booking.id.hex[:6]}-{idx+1}"
            ticket = Ticket(
                item_id=item.id,
                type=TicketType.flight,
                code=code,
                issued_at=datetime.now(UTC),
            )
            self.db.add(ticket)
            tickets.append(ticket)

        await self.db.commit()
        await self.db.refresh(booking)
        await self.db.refresh(item)
        for t in tickets:
            await self.db.refresh(t)

        return FlightBookingResult(
            booking=BookingRead.model_validate(booking, from_attributes=True),
            item=BookingItemRead.model_validate(item, from_attributes=True),  # type: ignore[name-defined]
            tickets=[TicketRead.model_validate(t, from_attributes=True) for t in tickets],  # type: ignore[name-defined]
        )

    # ---------- FLOW: ĐẶT PHÒNG KHÁCH SẠN ----------

    async def create_hotel_booking(
        self, payload: HotelBookingRequest
    ) -> HotelBookingResult:
        """
        Đặt phòng khách sạn dựa trên room + rate_plan + khoảng ngày.
        - Check RoomInventoryDaily đảm bảo đủ allotment trong toàn bộ khoảng ngày.
        - Tính tổng giá base_price * số đêm * số phòng.
        """

        if payload.check_in >= payload.check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngày check-out phải sau ngày check-in",
            )

        hotel = await self.db.get(Hotel, payload.hotel_id)
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy khách sạn",
            )

        room = await self.db.get(HotelRoom, payload.room_id)
        if not room or room.hotel_id != hotel.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phòng không thuộc khách sạn này",
            )

        rate_plan = await self.db.get(RoomRatePlan, payload.rate_plan_id)
        if not rate_plan or rate_plan.hotel_id != hotel.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rate plan không thuộc khách sạn này",
            )

        # Check inventory từng ngày
        current = payload.check_in
        total_price = Decimal(0)
        nights = (payload.check_out - payload.check_in).days

        while current < payload.check_out:
            inv_stmt = (
                select(RoomInventoryDaily)
                .where(RoomInventoryDaily.room_id == room.id)
                .where(RoomInventoryDaily.rate_plan_id == rate_plan.id)
                .where(RoomInventoryDaily.stay_date == current)
            )
            inv_res = await self.db.exec(inv_stmt)
            inv = inv_res.first()
            if not inv:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Không tìm thấy inventory cho ngày {current}",
                )

            available = inv.allotment - inv.sold
            if available < payload.rooms or inv.stop_sell:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Không đủ phòng cho ngày {current}",
                )

            total_price += inv.base_price * payload.rooms
            current += timedelta(days=1)

        # Tạo Booking
        booking = Booking(
            user_id=payload.user_id,
            state=BookingState.pending_payment,
            currency_code=payload.currency_code,
            total_amount=total_price,
            quote_id=None,
            coupon_id=None,
        )
        self.db.add(booking)
        await self.db.flush()

        details_hotel: dict[str, Any] = {
            "type": "hotel",
            "hotel_id": str(hotel.id),
            "hotel_name": hotel.name,
            "room_id": str(room.id),
            "room_code": room.code,
            "rate_plan_id": str(rate_plan.id),
            "rate_plan_name": rate_plan.name,
            "check_in": payload.check_in.isoformat(),
            "check_out": payload.check_out.isoformat(),
            "nights": nights,
            "rooms": payload.rooms,
            "guests": payload.guests,
            "currency_code": payload.currency_code,
        }

        item = BookingItem(
            booking_id=booking.id,
            vertical="hotel",
            supplier_ref=str(hotel.id),
            details=details_hotel,
            price_amount=total_price,
        )
        self.db.add(item)

        await self.db.commit()
        await self.db.refresh(booking)
        await self.db.refresh(item)

        return HotelBookingResult(
            booking=BookingRead.model_validate(booking, from_attributes=True),
            item=BookingItemRead.model_validate(item, from_attributes=True),  # type: ignore[name-defined]
        )


