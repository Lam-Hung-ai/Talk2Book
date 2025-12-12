from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ReviewTargetType

if TYPE_CHECKING:
    from app.models.user import User


class Review(SQLModel, table=True):
    __tablename__ = "review"  # type: ignore
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_review_rating"),
        UniqueConstraint("user_id", "target_type", "target_key", name="uq_review_once"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    target_type: ReviewTargetType = Field(nullable=False)
    target_key: str = Field(nullable=False)
    rating: int = Field(nullable=False)
    comment: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    user: "User" = Relationship(back_populates="reviews")
