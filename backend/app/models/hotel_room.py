from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.room_inventory_daily import RoomInventoryDaily


class HotelRoom(SQLModel, table=True):
    __tablename__ = "hotel_room"  # type: ignore
    __table_args__ = (
        UniqueConstraint("hotel_id", "code", name="uq_room_hotel_code"),
        CheckConstraint("capacity > 0", name="chk_room_capacity"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    hotel_id: UUID = Field(foreign_key="hotel.id", nullable=False, ondelete="CASCADE")

    code: str | None = Field(default=None)
    capacity: int = Field(nullable=False)
    bed_config: str | None = Field(default=None)
    # Rich fields
    room_type: str | None = Field(default=None)              # Loại phòng (từ danh mục)
    area_sqm: float | None = Field(default=None)             # Diện tích m²
    view_type: str | None = Field(default=None)              # Tầm nhìn (từ danh mục)
    amenities: str | None = Field(default=None)              # JSON: ["Bồn tắm","Ban công",...]
    service_package: str | None = Field(default=None)        # Gói dịch vụ (từ danh mục)
    cancellation_policy: str | None = Field(default=None)    # Chính sách hoàn hủy
    description: str | None = Field(default=None)            # Mô tả phòng
    images: str | None = Field(default=None)                 # JSON: ["url1","url2",...]

    # Rich fields
    room_type: str | None = Field(default=None)              # Loại phòng (từ danh mục)
    area_sqm: float | None = Field(default=None)             # Diện tích m²
    view_type: str | None = Field(default=None)              # Tầm nhìn (từ danh mục)
    amenities: str | None = Field(default=None)              # JSON: ["Bồn tắm","Ban công",...]
    service_package: str | None = Field(default=None)        # Gói dịch vụ (từ danh mục)
    cancellation_policy: str | None = Field(default=None)    # Chính sách hoàn hủy
    description: str | None = Field(default=None)            # Mô tả phòng
    images: str | None = Field(default=None)                 # JSON: ["url1","url2",...]

    # Relationships
    hotel: "Hotel" = Relationship(back_populates="rooms")
    inventory_items: list["RoomInventoryDaily"] = Relationship(back_populates="room")
