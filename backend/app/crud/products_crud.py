from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.products import Product


class ProductCRUD:
    """CRUD operations for Product"""

    @staticmethod
    def create(
        session: Session,
        code: str,
        name: str,
        description: Optional[str] = None,
        service_type: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        active: bool = True,
    ) -> Product:
        p = Product(
            code=code,
            name=name,
            description=description,
            service_type=service_type,
            duration_minutes=duration_minutes,
            active=active,
            created_at=datetime.utcnow(),
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        return p

    @staticmethod
    def get_by_id(session: Session, product_id: UUID) -> Optional[Product]:
        return session.get(Product, product_id)

    @staticmethod
    def get_by_code(session: Session, code: str) -> Optional[Product]:
        statement = select(Product).where(Product.code == code)
        return session.exec(statement).first()

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        statement = select(Product).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(session: Session, product_id: UUID, **kwargs) -> Optional[Product]:
        p = session.get(Product, product_id)
        if not p:
            return None
        for k, v in kwargs.items():
            if hasattr(p, k) and v is not None:
                setattr(p, k, v)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p

    @staticmethod
    def delete(session: Session, product_id: UUID) -> bool:
        p = session.get(Product, product_id)
        if not p:
            return False
        session.delete(p)
        session.commit()
        return True
