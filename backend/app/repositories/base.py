from typing import Generic, TypeVar, Type, Optional, Sequence, Any

from sqlmodel import SQLModel, select, func
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[ModelType]:
        return await self.db.get(self.model, id)
    
    async def get_or_404(self, id: Any, detail: str = "Not Found") -> ModelType:
        obj = await self.db.get(self.model, id)

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

        return obj
    
    async def get_multi(self, *, skip: int = 0, limit: int = 100, **filters) -> Sequence[ModelType]:
        query = select(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        return (await self.db.exec(query.offset(skip).limit(limit))).all()

    async def get_count(self, **filters) -> int:

        statement = select(func.count()).select_from(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                statement = statement.where(getattr(self.model, key) == value)
        count = (await self.db.exec(statement)).one()
        return count
    
    async def create(self, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:

        db_obj = self.model.model_validate(obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj
    
    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_obj, key) and value is not None:
                setattr(db_obj, key, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj
    
    async def delete(self, id: Any) -> None:
        db_obj = await self.get_or_404(id)
        await self.db.delete(db_obj)
        await self.db.commit()
        return
