"""
Budget Model
"""
from typing import TYPE_CHECKING, Optional
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import String, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.postgres import Base

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.category import Category


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    limit_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="budgets")
    category: Mapped["Category"] = relationship("Category")