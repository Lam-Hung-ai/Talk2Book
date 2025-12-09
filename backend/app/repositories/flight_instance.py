from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.flight_instance import FlightInstance
from app.repositories.base import BaseCRUD
from app.schemas.flight_instance import FlightInstanceCreate, FlightInstanceUpdate


class FlightInstanceRepository(
    BaseCRUD[FlightInstance, FlightInstanceCreate, FlightInstanceUpdate]
):
    def __init__(self, db: AsyncSession):
        super().__init__(FlightInstance, db)

    async def list_filtered(
        self,
        *,
        limit: int,
        offset: int,
        schedule_id: UUID | None,
        flight_date: date | None,
        status: str | None,
    ) -> Sequence[FlightInstance]:
        query = select(FlightInstance)
        if schedule_id:
            query = query.where(FlightInstance.schedule_id == schedule_id)
        if flight_date:
            query = query.where(FlightInstance.flight_date == flight_date)
        if status:
            query = query.where(FlightInstance.status == status)
        result = await self.db.exec(query.offset(offset).limit(limit))
        return result.all()

