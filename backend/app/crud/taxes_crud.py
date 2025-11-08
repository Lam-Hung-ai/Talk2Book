from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.taxes import Tax


class TaxesCRUD:
    """CRUD operations for Tax"""

    @staticmethod
    def create(
        session: Session,
        code: str,
        name: str,
        percent: Optional[float] = None,
        amount: Optional[float] = None,
        currency_code: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Tax:
        tax = Tax(
            code=code,
            name=name,
            percent=percent,
            amount=amount,
            currency_code=currency_code,
            description=description,
            created_at=datetime.utcnow(),
        )
        session.add(tax)
        session.commit()
        session.refresh(tax)
        return tax

    @staticmethod
    def get_by_id(session: Session, tax_id: UUID) -> Optional[Tax]:
        return session.get(Tax, tax_id)

    @staticmethod
    def get_by_code(session: Session, code: str) -> Optional[Tax]:
        statement = select(Tax).where(Tax.code == code)
        return session.exec(statement).first()

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Tax]:
        statement = select(Tax).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(session: Session, tax_id: UUID, **kwargs) -> Optional[Tax]:
        tax = session.get(Tax, tax_id)
        if not tax:
            return None
        for k, v in kwargs.items():
            if hasattr(tax, k) and v is not None:
                setattr(tax, k, v)
        session.add(tax)
        session.commit()
        session.refresh(tax)
        return tax

    @staticmethod
    def delete(session: Session, tax_id: UUID) -> bool:
        tax = session.get(Tax, tax_id)
        if not tax:
            return False
        session.delete(tax)
        session.commit()
        return True
