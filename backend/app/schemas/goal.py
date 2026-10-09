"""
Savings Goal Pydantic Schemas
"""
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class GoalBase(BaseModel):
    """Base savings goal schema."""
    name: str = Field(..., min_length=1, max_length=80)
    target_amount: Decimal = Field(..., gt=0, decimal_places=2)
    auto_sweep_pct: float = Field(default=0.0, ge=0, le=100)
    deadline: Optional[date] = None


class GoalCreate(GoalBase):
    """Goal creation schema."""
    pass


class GoalUpdate(BaseModel):
    """Goal update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=80)
    target_amount: Optional[condecimal(gt=0, decimal_places=2)] = None
    auto_sweep_pct: Optional[float] = Field(None, ge=0, le=100)
    deadline: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|ACHIEVED|PAUSED)$")


class GoalResponse(GoalBase):
    """Goal response schema."""
    id: str
    user_id: str
    current_amount: Decimal
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoalWithProgress(GoalResponse):
    """Goal with progress calculation."""
    progress_percentage: float = 0.0
    remaining_amount: Decimal = Decimal('0.00')
    days_remaining: Optional[int] = None
    monthly_sweep_amount: Optional[Decimal] = None