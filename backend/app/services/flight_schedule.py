from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.provider import Provider
from app.models.route import Route
from app.repositories.flight_schedule import FlightScheduleRepository
from app.schemas.flight_schedule import (
    FlightScheduleCreate,
    FlightScheduleRead,
    FlightScheduleUpdate,
)


class FlightScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FlightScheduleRepository(db)

    async def _ensure_provider(self, provider_id: UUID) -> None:
        provider = await self.db.get(Provider, provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider {provider_id} does not exist",
            )

    async def _ensure_route(self, route_id: UUID) -> None:
        route = await self.db.get(Route, route_id)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Route {route_id} does not exist",
            )

    async def create_schedule(
        self, payload: FlightScheduleCreate
    ) -> FlightScheduleRead:
        await self._ensure_provider(payload.provider_id)
        await self._ensure_route(payload.route_id)

        schedule = await self.repo.create(payload)
        return FlightScheduleRead.model_validate(schedule, from_attributes=True)

    async def list_schedules(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        provider_id: UUID | None = None,
        route_id: UUID | None = None,
        dow: int | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size

        if q:
            items = await self.repo.search(
                query=q,
                search_columns=["flight_number", "aircraft_code"],
                skip=skip,
                limit=page_size,
            )
            total = await self.repo.count_search(
                query=q,
                search_columns=["flight_number", "aircraft_code"],
            )
        else:
            items = await self.repo.list_filtered(
                limit=page_size,
                offset=skip,
                provider_id=provider_id,
                route_id=route_id,
                dow=dow,
            )
            total = await self.repo.get_count()

        return {
            "items": [FlightScheduleRead.model_validate(s, from_attributes=True) for s in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_schedule(self, schedule_id: UUID) -> FlightScheduleRead:
        schedule = await self.repo.get_or_404(schedule_id, detail="Flight schedule not found")
        return FlightScheduleRead.model_validate(schedule, from_attributes=True)

    async def update_schedule(
        self, schedule_id: UUID, payload: FlightScheduleUpdate
    ) -> FlightScheduleRead:
        schedule = await self.repo.get_or_404(schedule_id, detail="Flight schedule not found")

        data = payload.model_dump(exclude_unset=True)
        if "provider_id" in data:
            await self._ensure_provider(data["provider_id"])
        if "route_id" in data:
            await self._ensure_route(data["route_id"])

        updated = await self.repo.update(schedule, data)
        return FlightScheduleRead.model_validate(updated, from_attributes=True)

    async def delete_schedule(self, schedule_id: UUID) -> None:
        await self.repo.delete(schedule_id)

