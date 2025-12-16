# app/services/search.py
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.airport import Airport
from app.models.city import City
from app.models.flight_instance import FlightInstance
from app.models.flight_schedule import FlightSchedule
from app.models.hotel import Hotel
from app.models.hotel_room import HotelRoom
from app.models.provider import Provider
from app.models.room_inventory_daily import RoomInventoryDaily
from app.models.room_rate_plan import RoomRatePlan
from app.models.route import Route
from app.models.seat_inventory import SeatInventory
from app.schemas.search import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightSearchResult,
    HotelAvailabilityRequest,
    HotelAvailabilityResponse,
    HotelSearchRequest,
    HotelSearchResponse,
    HotelSearchResult,
    RoomAvailabilityDetail,
)

# from app.services.airport import AirportService


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_flights(
        self, request: FlightSearchRequest, page: int = 1, page_size: int = 20
    ) -> FlightSearchResponse:
        """
        Tìm chuyến bay: Join Route -> Schedule -> Instance và check SeatInventory
        """
        # Validate origin và destination airports
        origin_airport = await self.db.exec(
            select(Airport).where(Airport.iata == request.origin.upper())
        )
        origin_airport = origin_airport.first()
        if not origin_airport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sân bay đi với mã {request.origin}",
            )

        dest_airport = await self.db.exec(
            select(Airport).where(Airport.iata == request.destination.upper())
        )
        dest_airport = dest_airport.first()
        if not dest_airport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sân bay đến với mã {request.destination}",
            )

        if request.origin.upper() == request.destination.upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sân bay đi và đến không thể giống nhau",
            )

        # Tìm route
        route = await self.db.exec(
            select(Route)
            .where(Route.origin == request.origin.upper())
            .where(Route.destination == request.destination.upper())
        )
        route = route.first()
        if not route:
            return FlightSearchResponse(
                items=[], total=0, page=page, page_size=page_size, total_pages=0
            )

        # Tìm flight instances cho ngày đó
        instances_stmt = (
            select(
                FlightInstance,
                FlightSchedule,
                Provider,
                Route,
            )
            .join(FlightSchedule, FlightInstance.schedule_id == FlightSchedule.id)  # type: ignore
            .join(Provider, FlightSchedule.provider_id == Provider.id)  # type: ignore
            .join(Route, FlightSchedule.route_id == Route.id)  # type: ignore
            .where(FlightInstance.flight_date == request.flight_date)
            .where(Route.id == route.id)
        )

        # Phân trang
        skip = (page - 1) * page_size
        instances_stmt = instances_stmt.offset(skip).limit(page_size * 2)  # Lấy thêm để filter sau

        results = await self.db.exec(instances_stmt)
        instances_data = results.all()

        # Lấy seat inventory cho mỗi instance
        items: list[FlightSearchResult] = []
        for instance, schedule, provider, route_obj in instances_data:
            # Lấy seat inventory với filter
            seat_stmt = select(SeatInventory).where(SeatInventory.instance_id == instance.id)
            if request.cabin:
                seat_stmt = seat_stmt.where(SeatInventory.cabin == request.cabin)
            if request.fare_bucket:
                seat_stmt = seat_stmt.where(SeatInventory.fare_bucket == request.fare_bucket)
            seats = await self.db.exec(seat_stmt)
            seat_list = seats.all()

            if not seat_list:
                # Không có seat inventory, bỏ qua
                continue

            # Tìm seat có ghế trống
            found_available = False
            for seat in seat_list:
                available = seat.total_seats - seat.sold_seats - seat.held_seats
                if available > 0:
                    items.append(
                        FlightSearchResult(
                            instance_id=instance.id,
                            flight_number=schedule.flight_number,
                            provider_name=provider.display_name,
                            origin=route_obj.origin,
                            destination=route_obj.destination,
                            dep_datetime=instance.dep_datetime,
                            arr_datetime=instance.arr_datetime,
                            flight_date=instance.flight_date,
                            status=instance.status,
                            available_seats=available,
                            cabin=seat.cabin,
                            fare_bucket=seat.fare_bucket,
                            total_seats=seat.total_seats,
                            sold_seats=seat.sold_seats,
                        )
                    )
                    found_available = True
                    break  # Chỉ lấy 1 record đầu tiên có ghế trống

        # Giới hạn số lượng items theo page_size
        items = items[:page_size]

        return FlightSearchResponse(
            items=items,
            total=len(items),  # Số lượng thực tế có ghế trống trong page này
            page=page,
            page_size=page_size,
            total_pages=(len(items) + page_size - 1) // page_size if items else 0,
        )

    async def search_hotels(
        self, request: HotelSearchRequest, page: int = 1, page_size: int = 20
    ) -> HotelSearchResponse:
        """
        Tìm khách sạn: Quét RoomInventoryDaily trong khoảng ngày, xem có phòng nào còn trống liên tiếp không
        """
        if request.check_in >= request.check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngày check-out phải sau ngày check-in",
            )

        # Validate city
        city = await self.db.get(City, request.city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy thành phố với ID {request.city_id}",
            )

        # Tính số đêm
        nights = (request.check_out - request.check_in).days

        # Lấy tất cả hotels trong city
        hotels_stmt = select(Hotel).where(Hotel.city_id == request.city_id)
        skip = (page - 1) * page_size
        hotels_stmt = hotels_stmt.offset(skip).limit(page_size)
        hotels = await self.db.exec(hotels_stmt)
        hotel_list = hotels.all()

        items: list[HotelSearchResult] = []

        for hotel in hotel_list:
            # Lấy provider
            provider = await self.db.get(Provider, hotel.provider_id)
            provider_name = provider.display_name if provider else "Unknown"

            # Lấy tất cả rooms của hotel
            rooms_stmt = select(HotelRoom).where(HotelRoom.hotel_id == hotel.id)
            rooms = await self.db.exec(rooms_stmt)
            room_list = rooms.all()

            if not room_list:
                continue

            # Với mỗi room, check inventory trong khoảng ngày
            available_rooms_count = 0
            min_price: Decimal | None = None
            currency_code: str | None = None

            for room in room_list:
                # Lấy tất cả rate plans cho room này
                rate_plans_stmt = select(RoomRatePlan).where(RoomRatePlan.hotel_id == hotel.id)
                rate_plans = await self.db.exec(rate_plans_stmt)
                rate_plan_list = rate_plans.all()

                for rate_plan in rate_plan_list:
                    # Check inventory cho từng ngày trong khoảng
                    all_dates_available = True
                    total_price = Decimal(0)
                    room_currency = rate_plan.currency_code

                    current_date = request.check_in
                    while current_date < request.check_out:
                        inventory_stmt = (
                            select(RoomInventoryDaily)
                            .where(RoomInventoryDaily.room_id == room.id)
                            .where(RoomInventoryDaily.rate_plan_id == rate_plan.id)
                            .where(RoomInventoryDaily.stay_date == current_date)
                        )
                        inventory_result = await self.db.exec(inventory_stmt)
                        inventory = inventory_result.first()

                        if not inventory:
                            all_dates_available = False
                            break

                        # Check còn phòng không (allotment - sold > 0) và không stop_sell
                        available = inventory.allotment - inventory.sold
                        if available <= 0 or inventory.stop_sell:
                            all_dates_available = False
                            break

                        # Check capacity (số khách)
                        if room.capacity < request.guests:
                            all_dates_available = False
                            break

                        total_price += inventory.base_price
                        current_date += timedelta(days=1)

                    if all_dates_available:
                        # Phòng này có sẵn cho toàn bộ khoảng ngày
                        available_rooms_count += 1
                        if min_price is None or total_price < min_price:
                            min_price = total_price
                            currency_code = room_currency

            # Chỉ thêm hotel nếu có ít nhất số phòng yêu cầu
            if available_rooms_count >= request.rooms:
                items.append(
                    HotelSearchResult(
                        hotel_id=hotel.id,
                        hotel_name=hotel.name,
                        provider_name=provider_name,
                        city_name=city.name,
                        star_rating=hotel.star_rating,
                        address=hotel.address,
                        lat=hotel.lat,
                        lng=hotel.lng,
                        available_rooms=available_rooms_count,
                        min_price=min_price,
                        currency_code=currency_code,
                    )
                )

        # Đếm total hotels trong city
        total_stmt = select(func.count()).select_from(Hotel).where(Hotel.city_id == request.city_id)
        total_result = await self.db.exec(total_stmt)
        total = total_result.one() or 0

        return HotelSearchResponse(
            items=items,
            total=len(items),  # Số lượng thực tế có phòng trống
            page=page,
            page_size=page_size,
            total_pages=(len(items) + page_size - 1) // page_size if items else 0,
        )

    async def get_hotel_availability(
        self, hotel_id: UUID, request: HotelAvailabilityRequest
    ) -> HotelAvailabilityResponse:
        """
        Chi tiết phòng & Giá: List các loại phòng (Room) + Giá tổng cho khoảng ngày đã chọn
        """
        if request.check_in >= request.check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngày check-out phải sau ngày check-in",
            )

        # Validate hotel
        hotel = await self.db.get(Hotel, hotel_id)
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khách sạn với ID {hotel_id}",
            )

        # Tính số đêm
        nights = (request.check_out - request.check_in).days

        # Lấy tất cả rooms của hotel
        rooms_stmt = select(HotelRoom).where(HotelRoom.hotel_id == hotel_id)
        rooms = await self.db.exec(rooms_stmt)
        room_list = rooms.all()

        room_details: list[RoomAvailabilityDetail] = []

        for room in room_list:
            # Lấy tất cả rate plans cho room này
            rate_plans_stmt = select(RoomRatePlan).where(RoomRatePlan.hotel_id == hotel_id)
            rate_plans = await self.db.exec(rate_plans_stmt)
            rate_plan_list = rate_plans.all()

            for rate_plan in rate_plan_list:
                # Check inventory cho từng ngày trong khoảng
                all_dates_available = True
                total_price = Decimal(0)
                daily_prices: list[Decimal] = []

                current_date = request.check_in
                while current_date < request.check_out:
                    inventory_stmt = (
                        select(RoomInventoryDaily)
                        .where(RoomInventoryDaily.room_id == room.id)
                        .where(RoomInventoryDaily.rate_plan_id == rate_plan.id)
                        .where(RoomInventoryDaily.stay_date == current_date)
                    )
                    inventory_result = await self.db.exec(inventory_stmt)
                    inventory = inventory_result.first()

                    if not inventory:
                        all_dates_available = False
                        break

                    # Check còn phòng không và không stop_sell
                    available = inventory.allotment - inventory.sold
                    if available <= 0 or inventory.stop_sell:
                        all_dates_available = False
                        break

                    total_price += inventory.base_price
                    daily_prices.append(inventory.base_price)
                    current_date += timedelta(days=1)

                if all_dates_available:
                    # Tính số phòng còn trống (lấy min của tất cả các ngày)
                    min_available = float("inf")
                    current_date = request.check_in
                    while current_date < request.check_out:
                        inventory_stmt = (
                            select(RoomInventoryDaily)
                            .where(RoomInventoryDaily.room_id == room.id)
                            .where(RoomInventoryDaily.rate_plan_id == rate_plan.id)
                            .where(RoomInventoryDaily.stay_date == current_date)
                        )
                        inventory_result = await self.db.exec(inventory_stmt)
                        inventory = inventory_result.first()
                        if inventory:
                            available = inventory.allotment - inventory.sold
                            min_available = min(min_available, available)
                        current_date += timedelta(days=1)

                    price_per_night = total_price / nights if nights > 0 else Decimal(0)

                    room_details.append(
                        RoomAvailabilityDetail(
                            room_id=room.id,
                            room_code=room.code,
                            capacity=room.capacity,
                            bed_config=room.bed_config,
                            rate_plan_id=rate_plan.id,
                            rate_plan_name=rate_plan.name,
                            meal_plan=rate_plan.meal_plan,
                            available_rooms=int(min_available) if min_available != float("inf") else 0,
                            total_price=total_price,
                            price_per_night=price_per_night,
                            currency_code=rate_plan.currency_code,
                            nights=nights,
                        )
                    )

        return HotelAvailabilityResponse(
            hotel_id=hotel.id,
            hotel_name=hotel.name,
            check_in=request.check_in,
            check_out=request.check_out,
            nights=nights,
            rooms=room_details,
        )

