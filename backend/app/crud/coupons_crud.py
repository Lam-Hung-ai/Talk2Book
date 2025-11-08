from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.coupons import Coupon


class CouponCRUD:
    """CRUD operations for Coupon"""

    @staticmethod
    def create(
        session: Session,
        code: str,
        description: Optional[str] = None,
        percent: Optional[float] = None,
        amount: Optional[float] = None,
        currency_code: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        usage_limit: Optional[int] = None,
        per_user_limit: Optional[int] = None,
        active: bool = True,
    ) -> Coupon:
        coupon = Coupon(
            code=code,
            description=description,
            percent=percent,
            amount=amount,
            currency_code=currency_code,
            start_at=start_at,
            end_at=end_at,
            usage_limit=usage_limit,
            per_user_limit=per_user_limit,
            active=active,
            created_at=datetime.utcnow(),
        )
        session.add(coupon)
        session.commit()
        session.refresh(coupon)
        return coupon

    @staticmethod
    def get_by_id(session: Session, coupon_id: UUID) -> Optional[Coupon]:
        return session.get(Coupon, coupon_id)

    @staticmethod
    def get_by_code(session: Session, code: str) -> Optional[Coupon]:
        statement = select(Coupon).where(Coupon.code == code)
        return session.exec(statement).first()

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Coupon]:
        statement = select(Coupon).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        coupon_id: UUID,
        **kwargs,
    ) -> Optional[Coupon]:
        coupon = session.get(Coupon, coupon_id)
        if not coupon:
            return None
        for k, v in kwargs.items():
            if hasattr(coupon, k) and v is not None:
                setattr(coupon, k, v)
        session.add(coupon)
        session.commit()
        session.refresh(coupon)
        return coupon

    @staticmethod
    def delete(session: Session, coupon_id: UUID) -> bool:
        coupon = session.get(Coupon, coupon_id)
        if not coupon:
            return False
        session.delete(coupon)
        session.commit()
        return True
