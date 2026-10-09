"""
Repository Pattern for Budget Data Access
"""
from backend.app.db.postgres import get_db, Base
from backend.app.models.budget import Budget
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import select, and_
from datetime import date

if TYPE_CHECKING:
    from backend.app.models.user import User


class BudgetRepo:
    """Repository for Budget aggregates."""

    @staticmethod
    def get_by_id(db, budget_id: str) -> Optional[Budget]:
        """Get budget by ID."""
        result = db.execute(select(Budget).where(Budget.id == budget_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_user_and_month(
        db, user_id: str, month: date
    ) -> List[Budget]:
        """Get all budgets for a user for a specific month."""
        query = select(Budget).where(
            Budget.user_id == user_id,
            Budget.month == month
        )
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_by_user(db, user_id: str) -> List[Budget]:
        """Get all budgets for a user."""
        query = select(Budget).where(Budget.user_id == user_id).order_by(Budget.month.desc())
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_by_category(db, user_id: str, category_id: int, month: date) -> Optional[Budget]:
        """Get budget for a specific user/category/month."""
        result = db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.month == month
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def create(db, budget_dict) -> Budget:
        """Create a new budget."""
        budget = Budget(**budget_dict)
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

    @staticmethod
    def update(db, budget: Budget, updates: dict) -> Budget:
        """Update budget fields."""
        for field, value in updates.items():
            setattr(budget, field, value)
        db.commit()
        db.refresh(budget)
        return budget

    @staticmethod
    def delete(db, budget: Budget) -> None:
        """Delete a budget."""
        db.delete(budget)
        db.commit()

    @staticmethod
    def list_all(db, skip: int = 0, limit: int = 100) -> List[Budget]:
        """List all budgets with pagination."""
        query = select(Budget).offset(skip).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_with_utilization(db, budget_id: str) -> Optional[dict]:
        """Get budget with utilization data (placeholder - would join with transactions)."""
        budget = BudgetRepo.get_by_id(db, budget_id)
        if not budget:
            return None
        # This would be computed by BudgetService
        return {
            "budget_id": budget.id,
            "category_id": budget.category_id,
            "limit_amount": budget.limit_amount,
            "spent_amount": 0,
            "utilization_percentage": 0.0,
            "remaining_amount": budget.limit_amount,
            "is_over_budget": False,
            "projected_end_amount": 0.0,
            "days_elapsed": 0,
            "days_in_month": 0,
            "will_breach": False,
        }