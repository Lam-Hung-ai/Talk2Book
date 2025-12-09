from uuid import UUID

from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.seat_inventory import SeatInventory
from app.models.enums import CabinType, FareBucketType
from app.schemas.seat_inventory import SeatInventoryCreate, SeatInventoryUpdate


class SeatInventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_one(
        self, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
    ) -> SeatInventory | None:
        stmt = select(SeatInventory).where(
            and_(
                SeatInventory.instance_id == instance_id,
                SeatInventory.cabin == cabin,
                SeatInventory.fare_bucket == fare_bucket,
            )
        )
        return (await self.db.exec(stmt)).first()

    async def create(self, data: SeatInventoryCreate) -> SeatInventory:
        existing = await self._get_one(data.instance_id, data.cabin, data.fare_bucket)
        if existing:
            return existing
        obj = SeatInventory.model_validate(data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(
        self, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
    ) -> SeatInventory | None:
        return await self._get_one(instance_id, cabin, fare_bucket)

    async def update(
        self,
        db_obj: SeatInventory,
        data: SeatInventoryUpdate,
    ) -> SeatInventory:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(
        self, instance_id: UUID, cabin: CabinType, fare_bucket: FareBucketType
    ) -> bool:
        obj = await self._get_one(instance_id, cabin, fare_bucket)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

