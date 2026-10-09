"""
Category Repository
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.category import Category


class CategoryRepo:
    """Repository for Category data access."""

    @staticmethod
    def get_all(db: Session) -> List[Category]:
        """Get all categories."""
        result = db.execute(select(Category).order_by(Category.id))
        return list(result.scalars().all())

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        result = db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_kind(db: Session, kind: str) -> List[Category]:
        """Get categories by kind (INCOME/EXPENSE)."""
        result = db.execute(select(Category).where(Category.kind == kind))
        return list(result.scalars().all())

    @staticmethod
    def get_defaults(db: Session) -> List[Category]:
        """Get default categories."""
        result = db.execute(select(Category).where(Category.is_default == True))
        return list(result.scalars().all())