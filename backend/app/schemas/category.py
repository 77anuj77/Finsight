"""
Category Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=60)
    kind: str = Field(..., pattern="^(INCOME|EXPENSE)$")
    is_default: bool = True


class CategoryCreate(CategoryBase):
    """Category creation schema."""
    pass


class CategoryUpdate(BaseModel):
    """Category update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=60)
    kind: Optional[str] = Field(None, pattern="^(INCOME|EXPENSE)$")
    is_default: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Category response schema."""
    id: int

    class Config:
        from_attributes = True