"""
Savings Goal Model
"""
from typing import TYPE_CHECKING, Optional
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.postgres import Base

if TYPE_CHECKING:
    from backend.app.models.user import User


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    auto_sweep_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="goals")