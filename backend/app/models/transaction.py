"""
Transaction Model
"""
from typing import TYPE_CHECKING, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.postgres import Base

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.account import Account
    from backend.app.models.budget import Budget


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payee: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    transacted_at: Mapped[datetime] = mapped_column(nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    flag_status: Mapped[str] = mapped_column(String(15), nullable=False, default="NORMAL")
    source: Mapped[str] = mapped_column(String(10), nullable=False, default="MANUAL")
    receipt_ref: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")