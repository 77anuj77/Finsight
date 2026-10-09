"""
Account Model
"""
from typing import TYPE_CHECKING, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.postgres import Base

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.transaction import Transaction as TransactionModel
    from backend.app.models.transfer import Transfer


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped["TransactionModel"] = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )
    outgoings: Mapped["Transfer"] = relationship(
        "Transfer",
        foreign_keys="Transfer.from_account_id",
        back_populates="from_account",
        cascade="all, delete-orphan"
    )
    incomings: Mapped["Transfer"] = relationship(
        "Transfer",
        foreign_keys="Transfer.to_account_id",
        back_populates="to_account",
        cascade="all, delete-orphan"
    )