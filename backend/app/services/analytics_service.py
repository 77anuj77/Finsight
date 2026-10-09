"""
Analytics Service - Business logic for analytics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

from backend.app.repositories.transaction_repo import TransactionRepo
from backend.app.repositories.account_repo import AccountRepo
from backend.app.repositories.budget_repo import BudgetRepo
from backend.app.models.transaction import Transaction
from backend.app.models.account import Account
from backend.app.models.budget import Budget


class AnalyticsService:
    """Service layer for analytics operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, user_id: str, month: date) -> Dict[str, Any]:
        """Get dashboard summary for a month."""
        month_start = month
        if month.month == 12:
            month_end = month.replace(year=month.year + 1, month=1)
        else:
            month_end = month.replace(month=month.month + 1)

        # Get transactions for the month
        transactions = TransactionRepo.get_by_user_and_date_range(
            self.db, user_id, month_start, month_end
        )

        # Calculate totals
        total_income = sum(Decimal(str(t.amount)) for t in transactions if t.type == "INCOME")
        total_expense = sum(Decimal(str(t.amount)) for t in transactions if t.type == "EXPENSE")
        net_savings = total_income - total_expense

        # Get account balances
        accounts = AccountRepo.get_by_user(self.db, user_id)
        total_balance = sum(acc.balance for acc in accounts)

        # Budget health
        budget_service = BudgetService(self.db)
        budgets = BudgetRepo.get_by_user_and_month(self.db, user_id, month)
        budget_alerts = budget_service.check_all_budgets(user_id)

        # Recent transactions (last 10)
        recent = sorted(transactions, key=lambda t: t.transacted_at, reverse=True)[:10]

        return {
            "month": month.isoformat(),
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_savings": float(net_savings),
            "total_balance": float(total_balance),
            "savings_rate": float(net_savings / total_income * 100) if total_income > 0 else 0,
            "budget_alerts_count": len(budget_alerts),
            "recent_transactions": [
                {
                    "id": t.id,
                    "amount": float(t.amount),
                    "type": t.type,
                    "payee": t.payee,
                    "transacted_at": t.transacted_at.isoformat() if hasattr(t.transacted_at, 'isoformat') else str(t.transacted_at),
                }
                for t in recent
            ],
        }

    def get_trends(self, user_id: str, months: int) -> List[Dict[str, Any]]:
        """Get monthly spending trends."""
        end_date = date.today().replace(day=1)
        start_date = end_date - timedelta(days=months * 30)

        transactions = TransactionRepo.get_by_user_and_date_range(
            self.db, user_id, start_date, end_date
        )

        # Group by month
        monthly_data = defaultdict(lambda: {"income": Decimal('0'), "expense": Decimal('0')})

        for t in transactions:
            if hasattr(t.transacted_at, 'month'):
                month_key = t.transacted_at.replace(day=1)
            else:
                # Handle string dates
                try:
                    dt = datetime.fromisoformat(str(t.transacted_at).replace('Z', '+00:00'))
                    month_key = dt.date().replace(day=1)
                except:
                    continue

            if t.type == "INCOME":
                monthly_data[month_key]["income"] += Decimal(str(t.amount))
            elif t.type == "EXPENSE":
                monthly_data[month_key]["expense"] += Decimal(str(t.amount))

        # Build result
        result = []
        current = start_date.replace(day=1)
        while current <= end_date:
            data = monthly_data.get(current, {"income": Decimal('0'), "expense": Decimal('0')})
            result.append({
                "month": current.isoformat(),
                "income": float(data["income"]),
                "expense": float(data["expense"]),
                "net": float(data["income"] - data["expense"]),
            })
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return result

    def get_category_breakdown(self, user_id: str, month: date) -> List[Dict[str, Any]]:
        """Get spending breakdown by category."""
        month_start = month
        if month.month == 12:
            month_end = month.replace(year=month.year + 1, month=1)
        else:
            month_end = month.replace(month=month.month + 1)

        transactions = TransactionRepo.get_by_user_and_date_range(
            self.db, user_id, month_start, month_end
        )

        category_totals = defaultdict(Decimal)
        for t in transactions:
            if t.type == "EXPENSE":
                category_totals[t.category_id] += Decimal(str(t.amount))

        total = sum(category_totals.values())

        return [
            {
                "category_id": cat_id,
                "amount": float(amount),
                "percentage": float(amount / total * 100) if total > 0 else 0,
            }
            for cat_id, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        ]

    def get_top_payees(self, user_id: str, month: date, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top payees by total amount."""
        month_start = month
        if month.month == 12:
            month_end = month.replace(year=month.year + 1, month=1)
        else:
            month_end = month.replace(month=month.month + 1)

        transactions = TransactionRepo.get_by_user_and_date_range(
            self.db, user_id, month_start, month_end
        )

        payee_totals = defaultdict(Decimal)
        for t in transactions:
            if t.type == "EXPENSE" and t.payee:
                payee_totals[t.payee] += Decimal(str(t.amount))

        return [
            {"payee": payee, "amount": float(amount)}
            for payee, amount in sorted(payee_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]

    def get_budget_vs_actual(self, user_id: str, month: date) -> List[Dict[str, Any]]:
        """Get budget vs actual comparison."""
        budgets = BudgetRepo.get_by_user_and_month(self.db, user_id, month)
        budget_service = BudgetService(self.db)

        return [budget_service.get_budget_utilization(b.id) for b in budgets]

    def get_net_worth(self, user_id: str) -> Dict[str, Any]:
        """Get current net worth."""
        accounts = AccountRepo.get_by_user(self.db, user_id)
        total = sum(acc.balance for acc in accounts)

        return {
            "total_net_worth": float(total),
            "accounts": [
                {"id": a.id, "name": a.name, "type": a.type, "balance": float(a.balance)}
                for a in accounts
            ],
        }

    def get_aggregate_analytics(self, month: str = None) -> Dict[str, Any]:
        """Get aggregate analytics across all users (admin)."""
        # This would be implemented with raw SQL for performance
        # Placeholder for now
        return {
            "total_users": 0,
            "total_transactions": 0,
            "total_volume": 0.0,
            "avg_budget_health": 0.0,
        }