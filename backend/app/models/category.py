"""
Category Model
"""
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.postgres import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)  # INCOME, EXPENSE
    is_default: Mapped[bool] = mapped_column(nullable=False, default=True)