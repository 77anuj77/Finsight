"""
Transaction Pydantic Schemas
"""
from pydantic import BaseModel, Field, condecimal
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    """Base transaction schema."""
    account_id: str
    category_id: int
    type: str = Field(..., pattern="^(INCOME|EXPENSE|TRANSFER)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payee: Optional[str] = Field(None, max_length=120)
    transacted_at: datetime
    notes: Optional[str] = None
    source: str = Field(default="MANUAL", pattern="^(MANUAL|IMPORT|AUTO)$")


class TransactionCreate(TransactionBase):
    """Transaction creation schema."""
    pass


class TransactionUpdate(BaseModel):
    """Transaction update schema."""
    account_id: Optional[str] = None
    category_id: Optional[int] = None
    type: Optional[str] = Field(None, pattern="^(INCOME|EXPENSE|TRANSFER)$")
    amount: Optional[condecimal(gt=0, decimal_places=2)] = None
    payee: Optional[str] = Field(None, max_length=120)
    transacted_at: Optional[datetime] = None
    notes: Optional[str] = None
    flag_status: Optional[str] = Field(None, pattern="^(NORMAL|SUSPICIOUS|REJECTED|CONFIRMED)$")


class TransactionResponse(TransactionBase):
    """Transaction response schema."""
    id: str
    user_id: str
    flag_status: str
    receipt_ref: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionList(BaseModel):
    """Paginated transaction list."""
    items: List[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int


class TransactionConfirm(BaseModel):
    """Transaction confirmation/rejection."""
    decision: str = Field(..., pattern="^(CONFIRMED|REJECTED)$")


class TransactionFilter(BaseModel):
    """Transaction filter parameters."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[int] = None
    type: Optional[str] = Field(None, pattern="^(INCOME|EXPENSE|TRANSFER)$")
    flag_status: Optional[str] = Field(None, pattern="^(NORMAL|SUSPICIOUS|REJECTED|CONFIRMED)$")
    account_id: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    page: int = 1
    size: int = 20