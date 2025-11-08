from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.coupon_redemptions import CouponRedemption


class CouponRedemptionCRUD:
    """CRUD operations for CouponRedemption"""

    @staticmethod
    def create(
        session: Session,
        coupon_id: UUID,
        user_id: Optional[UUID] = None,
        booking_id: Optional[UUID] = None,
        redeemed_at: Optional[datetime] = None,
        saved_amount: Optional[float] = None,
        currency_code: Optional[str] = None,
    ) -> CouponRedemption:
        cr = CouponRedemption(
            coupon_id=coupon_id,
            user_id=user_id,
            booking_id=booking_id,
            redeemed_at=redeemed_at or datetime.utcnow(),
            saved_amount=saved_amount,
            currency_code=currency_code,
        )
        session.add(cr)
        session.commit()
        session.refresh(cr)
        return cr

    @staticmethod
    def get_by_id(session: Session, cr_id: UUID) -> Optional[CouponRedemption]:
        return session.get(CouponRedemption, cr_id)

    @staticmethod
    def get_by_coupon(
        session: Session,
        coupon_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CouponRedemption]:
        statement = select(CouponRedemption).where(CouponRedemption.coupon_id == coupon_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_user(
        session: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CouponRedemption]:
        statement = select(CouponRedemption).where(CouponRedemption.user_id == user_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[CouponRedemption]:
        statement = select(CouponRedemption).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def delete(session: Session, cr_id: UUID) -> bool:
        cr = session.get(CouponRedemption, cr_id)
        if not cr:
            return False
        session.delete(cr)
        session.commit()
        return True
