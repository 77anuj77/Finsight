"""
Insights Service - AI-generated monthly financial insights
"""
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from backend.app.db.mongo import get_mongo_db
from backend.app.services.analytics_service import AnalyticsService
from backend.app.repositories.budget_repo import BudgetRepo
from backend.app.repositories.goal_repo import GoalRepo


class InsightsService:
    """Service for generating AI-powered financial insights."""

    def __init__(self, db: Session):
        self.db = db
        self.mongo_db = get_mongo_db()
        self.analytics_service = AnalyticsService(db)

    def get_latest(self, user_id: str, month: date) -> Optional[Dict[str, Any]]:
        """Get the latest insight for a user/month."""
        if self.mongo_db is None:
            return self._generate_fallback_insight(user_id, month)

        doc = self.mongo_db.ai_insights.find_one(
            {"user_id": user_id, "month_key": month.strftime("%Y-%m")},
            sort=[("generated_at", -1)]
        )

        if doc:
            doc["_id"] = str(doc["_id"])
            return doc

        # Generate if not exists
        return self.generate(user_id, month)

    def generate(self, user_id: str, month: date) -> Dict[str, Any]:
        """Generate a new monthly insight."""
        # Get data from analytics
        dashboard = self.analytics_service.get_dashboard(user_id, month)
        category_breakdown = self.analytics_service.get_category_breakdown(user_id, month)
        top_payees = self.analytics_service.get_top_payees(user_id, month, 5)
        budget_vs_actual = self.analytics_service.get_budget_vs_actual(user_id, month)

        # Generate insight
        insight = self._build_insight(user_id, month, dashboard, category_breakdown,
                                     top_payees, budget_vs_actual)

        # Save to MongoDB
        if self.mongo_db is not None:
            self.mongo_db.ai_insights.update_one(
                {"user_id": user_id, "month_key": month.strftime("%Y-%m")},
                {"$set": insight},
                upsert=True
            )

        return insight

    def _build_insight(self, user_id: str, month: date, dashboard: dict,
                      category_breakdown: list, top_payees: list,
                      budget_vs_actual: list) -> Dict[str, Any]:
        """Build the insight object."""
        month_str = month.strftime("%B %Y")
        total_income = dashboard.get("total_income", 0)
        total_expense = dashboard.get("total_expense", 0)
        net_savings = dashboard.get("net_savings", 0)
        savings_rate = dashboard.get("savings_rate", 0)

        # Top category
        top_category = category_breakdown[0] if category_breakdown else None
        top_cat_name = f"Category {top_category['category_id']}" if top_category else "None"
        top_cat_pct = top_category.get("percentage", 0) if top_category else 0

        # Budget alerts
        over_budget_cats = [b for b in budget_vs_actual if b.get("is_over_budget")]
        breach_warnings = [b for b in budget_vs_actual if b.get("will_breach")]

        # Build narrative
        summary = f"In {month_str}, you earned ₹{total_income:,.2f} and spent ₹{total_expense:,.2f}. "
        summary += f"Your net savings: ₹{net_savings:,.2f} ({savings_rate:.1f}% savings rate). "

        if top_category:
            summary += f"Your top spending category was {top_cat_name} at {top_cat_pct:.1f}% of expenses. "

        if over_budget_cats:
            summary += f"You exceeded budget in {len(over_budget_cats)} category(ies). "

        if breach_warnings:
            summary += f"{len(breach_warnings)} budget(s) are on track to breach. "

        # Recommendations
        recommendations = []
        if savings_rate < 20:
            recommendations.append("Aim to save at least 20% of your income. Consider reducing discretionary spending.")

        if top_category and top_cat_pct > 40:
            recommendations.append(f"Your {top_cat_name} spending is {top_cat_pct:.0f}% of expenses. "
                                 "Consider setting a stricter budget for this category.")

        if over_budget_cats:
            for b in over_budget_cats:
                recommendations.append(f"Budget exceeded for category {b['category_id']}: "
                                     f"spent ₹{b['spent_amount']:,.2f} of ₹{b['limit_amount']:,.2f} limit.")

        if breach_warnings:
            for b in breach_warnings:
                recommendations.append(f"Budget breach predicted for category {b['category_id']}. "
                                     f"Projected: ₹{b['projected_end_amount']:,.2f} vs limit ₹{b['limit_amount']:,.2f}.")

        if not recommendations:
            recommendations.append("Great job staying within your budgets! Consider increasing your savings rate.")

        # Warnings
        warnings = []
        if total_expense > total_income:
            warnings.append("You spent more than you earned this month.")

        if savings_rate < 10:
            warnings.append("Your savings rate is below 10%. Building an emergency fund should be a priority.")

        return {
            "user_id": user_id,
            "month_key": month.strftime("%Y-%m"),
            "generated_at": datetime.utcnow(),
            "summary": summary,
            "recommendations": recommendations,
            "warnings": warnings,
            "metrics": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_savings": net_savings,
                "savings_rate": savings_rate,
                "top_category": top_cat_name,
                "top_category_pct": top_cat_pct,
                "over_budget_count": len(over_budget_cats),
                "breach_warnings_count": len(breach_warnings),
            }
        }

    def _generate_fallback_insight(self, user_id: str, month: date) -> Dict[str, Any]:
        """Generate a basic insight without MongoDB."""
        dashboard = self.analytics_service.get_dashboard(user_id, month)
        category_breakdown = self.analytics_service.get_category_breakdown(user_id, month)
        top_payees = self.analytics_service.get_top_payees(user_id, month, 5)
        budget_vs_actual = self.analytics_service.get_budget_vs_actual(user_id, month)

        return self._build_insight(user_id, month, dashboard, category_breakdown,
                                  top_payees, budget_vs_actual)

    def get_history(self, user_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        """Get insight history for a user."""
        if self.mongo_db is None:
            return []

        cursor = self.mongo_db.ai_insights.find(
            {"user_id": user_id}
        ).sort("generated_at", -1).limit(limit)

        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)

        return results