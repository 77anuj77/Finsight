"""
Account Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AccountBase(BaseModel):
    """Base account schema."""
    name: str = Field(..., min_length=1, max_length=80)
    type: str = Field(..., pattern="^(CASH|BANK|UPI|CARD)$")
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")


class AccountCreate(AccountBase):
    """Account creation schema."""
    pass


class AccountUpdate(BaseModel):
    """Account update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=80)
    type: Optional[str] = Field(None, pattern="^(CASH|BANK|UPI|CARD)$")
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    """Account response schema."""
    id: str
    user_id: str
    balance: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AccountWithUser(AccountResponse):
    """Account with user info."""
    user_email: str
    user_name: str