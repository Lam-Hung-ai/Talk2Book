from collections.abc import Sequence
from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.flight_instance import FlightInstance
from app.models.flight_schedule import FlightSchedule
from app.repositories.flight_instance import FlightInstanceRepository
from app.schemas.flight_instance import (
    FlightInstanceCreate,
    FlightInstanceRead,
    FlightInstanceUpdate,
)


class FlightInstanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FlightInstanceRepository(db)

    async def _ensure_schedule(self, schedule_id: UUID) -> None:
        schedule = await self.db.get(FlightSchedule, schedule_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Schedule {schedule_id} does not exist",
            )

    @staticmethod
    def _validate_datetimes(dep, arr):
        if dep and arr and dep >= arr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="dep_datetime must be earlier than arr_datetime",
            )

    async def create_instance(
        self, payload: FlightInstanceCreate
    ) -> FlightInstanceRead:
        await self._ensure_schedule(payload.schedule_id)
        self._validate_datetimes(payload.dep_datetime, payload.arr_datetime)

        instance = await self.repo.create(payload)
        return FlightInstanceRead.model_validate(instance, from_attributes=True)

    async def list_instances(
        self,
        page: int = 1,
        page_size: int = 20,
        schedule_id: UUID | None = None,
        flight_date: date | None = None,
        status: str | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size
        items = await self.repo.list_filtered(
            limit=page_size,
            offset=skip,
            schedule_id=schedule_id,
            flight_date=flight_date,
            status=status,
        )
        total = await self.repo.get_count()

        return {
            "items": [FlightInstanceRead.model_validate(i, from_attributes=True) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_instance(self, instance_id: UUID) -> FlightInstanceRead:
        instance = await self.repo.get_or_404(instance_id, detail="Flight instance not found")
        return FlightInstanceRead.model_validate(instance, from_attributes=True)

    async def update_instance(
        self, instance_id: UUID, payload: FlightInstanceUpdate
    ) -> FlightInstanceRead:
        instance = await self.repo.get_or_404(instance_id, detail="Flight instance not found")

        data = payload.model_dump(exclude_unset=True)
        if "schedule_id" in data:
            await self._ensure_schedule(data["schedule_id"])
        self._validate_datetimes(
            data.get("dep_datetime", instance.dep_datetime),
            data.get("arr_datetime", instance.arr_datetime),
        )

        updated = await self.repo.update(instance, data)
        return FlightInstanceRead.model_validate(updated, from_attributes=True)

    async def delete_instance(self, instance_id: UUID) -> None:
        await self.repo.delete(instance_id)

