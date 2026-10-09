"""
Budget Service - Business logic for budgets
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, datetime
from typing import Optional

from backend.app.repositories.budget_repo import BudgetRepo
from backend.app.repositories.transaction_repo import TransactionRepo
from backend.app.services.notification_service import NotificationService
from backend.app.models.budget import Budget
from backend.app.models.transaction import Transaction


class BudgetService:
    """Service layer for budget operations."""

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService()

    def create_budget(self, budget_data: dict, user_id: str) -> Budget:
        """Create a new budget."""
        return BudgetRepo.create(self.db, {
            **budget_data,
            "user_id": user_id,
        })

    def get_budget_utilization(self, budget_id: str) -> dict:
        """Calculate budget utilization for a given budget."""
        budget = BudgetRepo.get_by_id(self.db, budget_id)
        if not budget:
            return None

        # Get transactions for this category and month
        month_start = budget.month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        transactions = TransactionRepo.get_by_category_and_date_range(
            self.db, budget.user_id, budget.category_id, month_start, month_end
        )

        spent = sum(Decimal(str(t.amount)) for t in transactions if t.type == "EXPENSE")
        utilization = float(spent / budget.limit_amount * 100) if budget.limit_amount > 0 else 0

        # Calculate projection
        days_in_month = (month_end - month_start).days
        days_elapsed = (date.today() - month_start).days
        days_elapsed = max(1, min(days_elapsed, days_in_month))

        daily_avg = spent / days_elapsed if days_elapsed > 0 else Decimal('0')
        projected_end = daily_avg * days_in_month

        return {
            "budget_id": budget.id,
            "category_id": budget.category_id,
            "limit_amount": budget.limit_amount,
            "spent_amount": spent,
            "utilization_percentage": round(utilization, 2),
            "remaining_amount": budget.limit_amount - spent,
            "is_over_budget": spent > budget.limit_amount,
            "projected_end_amount": projected_end,
            "days_elapsed": days_elapsed,
            "days_in_month": days_in_month,
            "will_breach": projected_end > budget.limit_amount and days_elapsed >= 5,
        }

    def check_all_budgets(self, user_id: str) -> list:
        """Check all budgets for a user and return alerts."""
        budgets = BudgetRepo.get_by_user(self.db, user_id)
        alerts = []

        for budget in budgets:
            utilization = self.get_budget_utilization(budget.id)
            if utilization and utilization["will_breach"]:
                alerts.append({
                    "budget_id": budget.id,
                    "category_id": budget.category_id,
                    "message": f"Budget for category {budget.category_id} will likely be exceeded. "
                              f"Projected: {utilization['projected_end_amount']:.2f}, "
                              f"Limit: {budget.limit_amount:.2f}",
                    "severity": "warning",
                })
                # Create notification
                self.notification_service.create_budget_alert(
                    user_id, budget.id, utilization
                )

        return alerts

    def get_monthly_budget_summary(self, user_id: str, month: date) -> list:
        """Get budget summary for a month."""
        budgets = BudgetRepo.get_by_user_and_month(self.db, user_id, month)
        summary = []

        for budget in budgets:
            utilization = self.get_budget_utilization(budget.id)
            summary.append({
                "budget": budget,
                "utilization": utilization,
            })

        return summary