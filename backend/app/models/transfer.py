"""
Transfer Model
"""
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.postgres import Base

if TYPE_CHECKING:
    from backend.app.models.account import Account


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[str] = mapped_column(primary_key=True)
    from_account_id: Mapped[str] = mapped_column(String(50), nullable=False)
    to_account_id: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[str] = mapped_column(String(20), nullable=False)  # NUMERIC
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    transferred_at: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    from_account: Mapped["Account"] = relationship(
        "Account", foreign_keys=[from_account_id], back_populates="outgoings"
    )
    to_account: Mapped["Account"] = relationship(
        "Account", foreign_keys=[to_account_id], back_populates="incomings"
    )