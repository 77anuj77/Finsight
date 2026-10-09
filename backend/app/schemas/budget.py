"""
Budget Pydantic Schemas
"""
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import date
from decimal import Decimal


class BudgetBase(BaseModel):
    """Base budget schema."""
    category_id: int
    month: date  # first day of month
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)


class BudgetCreate(BudgetBase):
    """Budget creation schema."""
    pass


class BudgetUpdate(BaseModel):
    """Budget update schema."""
    limit_amount: Optional[condecimal(gt=0, decimal_places=2)] = None


class BudgetResponse(BudgetBase):
    """Budget response schema."""
    id: str
    user_id: str
    created_at: date

    class Config:
        from_attributes = True


class BudgetWithUtilization(BudgetResponse):
    """Budget with utilization percentage."""
    spent_amount: Decimal = Decimal('0.00')
    utilization_percentage: float = 0.0
    remaining_amount: Decimal = Decimal('0.00')
    is_over_budget: bool = False
    projected_end_amount: Optional[Decimal] = None
    days_elapsed: int = 0
    days_in_month: int = 0