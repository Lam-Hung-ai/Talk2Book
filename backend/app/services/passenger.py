from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.passenger import PassengerRepository
from app.schemas.passenger import PassengerCreate, PassengerRead, PassengerUpdate


class PassengerService:
    def __init__(self, db: AsyncSession):
        self.repo = PassengerRepository(db)
        self.booking_repo = BookingRepository(db)

    async def create_passenger(self, passenger_in: PassengerCreate) -> PassengerRead:
        if not await self.booking_repo.get(passenger_in.booking_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )
        passenger = await self.repo.create(passenger_in)
        return PassengerRead.model_validate(passenger, from_attributes=True)

    async def get_passenger(self, passenger_id: UUID) -> PassengerRead:
        passenger = await self.repo.get_or_404(passenger_id, detail="Passenger not found")
        return PassengerRead.model_validate(passenger, from_attributes=True)

    async def list_passengers(
        self,
        page: int = 1,
        page_size: int = 50,
        booking_id: UUID | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        filters: dict[str, Any] = {}
        if booking_id is not None:
            filters["booking_id"] = booking_id

        passengers = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                PassengerRead.model_validate(p, from_attributes=True) for p in passengers
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_passenger(
        self, passenger_id: UUID, passenger_in: PassengerUpdate
    ) -> PassengerRead:
        passenger = await self.repo.get_or_404(passenger_id, detail="Passenger not found")
        updated = await self.repo.update(passenger, passenger_in)
        return PassengerRead.model_validate(updated, from_attributes=True)

    async def delete_passenger(self, passenger_id: UUID) -> None:
        await self.repo.delete(passenger_id)

    async def search_passengers(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        passengers = await self.repo.search(
            query=q,
            search_columns=["full_name"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["full_name"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )
        return {
            "items": [
                PassengerRead.model_validate(p, from_attributes=True) for p in passengers
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

