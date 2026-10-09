"""
Transfer Pydantic Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class TransferBase(BaseModel):
    """Base transfer schema."""
    from_account_id: str
    to_account_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    notes: Optional[str] = None


class TransferCreate(TransferBase):
    """Transfer creation schema."""
    pass


class TransferResponse(TransferBase):
    """Transfer response schema."""
    id: str
    transferred_at: datetime

    class Config:
        from_attributes = True