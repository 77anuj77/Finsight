"""
User Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation schema."""
    password: str
    role: str = "USER"
    monthly_income: float = 0.0
    currency: str = "INR"


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    monthly_income: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: str
    role: str
    currency: str
    monthly_income: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithStats(UserResponse):
    """User response with stats."""
    total_accounts: int = 0
    total_transactions: int = 0
    total_budgets: int = 0
    total_goals: int = 0