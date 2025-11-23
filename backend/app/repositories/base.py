from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession


class BaseCRUD[ModelType: SQLModel, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        return await self.db.get(self.model, id)

    async def get_or_404(self, id: Any, detail: str = "Not Found") -> ModelType:
        obj = await self.db.get(self.model, id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return obj

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> Sequence[ModelType]:
        query = select(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)

        query = query.offset(skip).limit(limit)
        result = await self.db.exec(query)
        return result.all()

    async def get_count(self, **filters: Any) -> int:
        statement = select(func.count()).select_from(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                statement = statement.where(getattr(self.model, key) == value)

        result = await self.db.exec(statement)
        return result.one()

    async def create(self, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        db_obj = self.model.model_validate(obj_in)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> None:
        db_obj = await self.get_or_404(id)
        await self.db.delete(db_obj)
        await self.db.commit()
