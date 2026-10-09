"""
Repository Pattern for Savings Goal Data Access
"""
from backend.app.db.postgres import get_db, Base
from backend.app.models.goal import SavingsGoal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import select
from decimal import Decimal

if TYPE_CHECKING:
    from backend.app.models.user import User


class GoalRepo:
    """Repository for Savings Goal aggregates."""

    @staticmethod
    def get_by_id(db, goal_id: str) -> Optional[SavingsGoal]:
        """Get goal by ID."""
        result = db.execute(select(SavingsGoal).where(SavingsGoal.id == goal_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_user(db, user_id: str, status: Optional[str] = None) -> List[SavingsGoal]:
        """Get all goals for a user, optionally filter by status."""
        query = select(SavingsGoal).where(SavingsGoal.user_id == user_id)
        if status:
            query = query.where(SavingsGoal.status == status)
        query = query.order_by(SavingsGoal.created_at.desc())
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def create(db, goal_dict) -> SavingsGoal:
        """Create a new savings goal."""
        goal = SavingsGoal(**goal_dict)
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update(db, goal: SavingsGoal, updates: dict) -> SavingsGoal:
        """Update goal fields."""
        for field, value in updates.items():
            setattr(goal, field, value)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete(db, goal: SavingsGoal) -> None:
        """Delete a savings goal."""
        db.delete(goal)
        db.commit()

    @staticmethod
    def increment_amount(db, goal: SavingsGoal, amount: Decimal) -> SavingsGoal:
        """Increment current amount (used for auto-sweep)."""
        goal.current_amount += amount
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def set_amount(db, goal: SavingsGoal, new_amount: Decimal) -> SavingsGoal:
        """Set current amount (for manual top-up)."""
        goal.current_amount = new_amount
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def check_achieved(db, goal: SavingsGoal) -> bool:
        """Check if goal has been achieved."""
        return goal.current_amount >= goal.target_amount

    @staticmethod
    def get_achievable(db, user_id: str) -> List[SavingsGoal]:
        """Get goals that are currently affordable (status ACTIVE and not achieved)."""
        query = select(SavingsGoal).where(
            SavingsGoal.user_id == user_id,
            SavingsGoal.status == 'ACTIVE',
            SavingsGoal.current_amount < SavingsGoal.target_amount
        )
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_with_progress(db, goal_id: str) -> Optional[dict]:
        """Get goal with progress calculation."""
        goal = GoalRepo.get_by_id(db, goal_id)
        if not goal:
            return None

        progress = float(goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining = goal.target_amount - goal.current_amount

        days_remaining = None
        if goal.deadline:
            from datetime import date
            delta = goal.deadline - date.today()
            days_remaining = delta.days if delta.days > 0 else 0

        monthly_sweep = None
        if goal.auto_sweep_pct > 0:
            # This would need user's monthly income
            monthly_sweep = None

        return {
            "goal_id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "auto_sweep_pct": goal.auto_sweep_pct,
            "deadline": goal.deadline,
            "status": goal.status,
            "progress_percentage": round(progress, 2),
            "remaining_amount": remaining,
            "days_remaining": days_remaining,
            "monthly_sweep_amount": monthly_sweep,
        }

    @staticmethod
    def trigger_sweep(db, goal: SavingsGoal) -> SavingsGoal:
        """Manually trigger auto-sweep for a goal."""
        # In a real implementation, this would calculate based on user's income
        # For now, just return the goal
        return goal