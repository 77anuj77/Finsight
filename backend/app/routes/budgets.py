"""
Budgets Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.repositories.budget_repo import BudgetRepo
from backend.app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetWithUtilization
from backend.app.models.user import User

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    month: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all budgets for the current user, optionally filtered by month."""
    if month is None:
        month = date.today().replace(day=1)
    return BudgetRepo.get_by_user_and_month(db, current_user.id, month)


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    budget = BudgetRepo.create(db, {
        **budget_data.model_dump(),
        "user_id": current_user.id,
    })
    return budget


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific budget."""
    budget = BudgetRepo.get_by_id(db, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a budget."""
    budget = BudgetRepo.get_by_id(db, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    updates = budget_data.model_dump(exclude_unset=True)
    return BudgetRepo.update(db, budget, updates)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget."""
    budget = BudgetRepo.get_by_id(db, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    BudgetRepo.delete(db, budget)


@router.get("/{budget_id}/utilization", response_model=BudgetWithUtilization)
def get_budget_utilization(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget with utilization data."""
    budget = BudgetRepo.get_by_id(db, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    return BudgetRepo.get_with_utilization(db, budget_id)