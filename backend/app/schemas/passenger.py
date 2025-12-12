from uuid import UUID

from pydantic import BaseModel, Field


class PassengerBase(BaseModel):
    booking_id: UUID
    full_name: str = Field(min_length=1)
    nationality: str | None = Field(default=None, max_length=2)


class PassengerCreate(PassengerBase):
    pass


class PassengerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1)
    nationality: str | None = Field(default=None, max_length=2)


class PassengerRead(PassengerBase):
    id: UUID

    class Config:
        from_attributes = True

