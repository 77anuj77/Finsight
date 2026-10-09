"""
Reports Service - Generate reports in various formats
"""
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import csv
import io

from backend.app.repositories.transaction_repo import TransactionRepo
from backend.app.repositories.account_repo import AccountRepo
from backend.app.repositories.budget_repo import BudgetRepo
from backend.app.repositories.goal_repo import GoalRepo
from backend.app.services.analytics_service import AnalyticsService


class ReportsService:
    """Service for generating financial reports."""

    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)

    def generate_monthly(self, user_id: str, month: date, format: str = "json") -> Dict[str, Any]:
        """Generate monthly report."""
        dashboard = self.analytics.get_dashboard(user_id, month)
        category_breakdown = self.analytics.get_category_breakdown(user_id, month)
        top_payees = self.analytics.get_top_payees(user_id, month, 10)
        budget_vs_actual = self.analytics.get_budget_vs_actual(user_id, month)

        report = {
            "user_id": user_id,
            "month": month.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": dashboard,
            "category_breakdown": category_breakdown,
            "top_payees": top_payees,
            "budget_vs_actual": budget_vs_actual,
        }

        if format == "json":
            return report
        elif format == "csv":
            return self._to_csv(report)
        elif format == "pdf":
            return self._to_pdf(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_yearly(self, user_id: str, year: int, format: str = "json") -> Dict[str, Any]:
        """Generate yearly report."""
        trends = self.analytics.get_trends(user_id, 12)
        net_worth = self.analytics.get_net_worth(user_id)

        # Aggregate monthly data
        total_income = sum(m["income"] for m in trends)
        total_expense = sum(m["expense"] for m in trends)

        report = {
            "user_id": user_id,
            "year": year,
            "generated_at": datetime.utcnow().isoformat(),
            "total_income": total_income,
            "total_expense": total_expense,
            "net_savings": total_income - total_expense,
            "monthly_breakdown": trends,
            "net_worth": net_worth,
        }

        if format == "json":
            return report
        elif format == "csv":
            return self._to_csv(report)
        elif format == "pdf":
            return self._to_pdf(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_transactions(
        self, user_id: str, start_date: Optional[date], end_date: Optional[date], format: str = "csv"
    ) -> Dict[str, Any]:
        """Export transactions for date range."""
        transactions = TransactionRepo.get_by_user_and_date_range(
            self.db, user_id, start_date, end_date
        )

        data = [
            {
                "id": t.id,
                "date": t.transacted_at.isoformat() if hasattr(t.transacted_at, 'isoformat') else str(t.transacted_at),
                "type": t.type,
                "amount": float(t.amount),
                "category_id": t.category_id,
                "payee": t.payee or "",
                "notes": t.notes or "",
                "flag_status": t.flag_status,
            }
            for t in transactions
        ]

        if format == "json":
            return {"transactions": data, "count": len(data)}
        elif format == "csv":
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return {"content": output.getvalue(), "filename": f"transactions_{user_id}.csv"}
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_csv(self, report: Dict) -> Dict[str, Any]:
        """Convert report to CSV format."""
        output = io.StringIO()
        # Flatten the report for CSV
        flat = self._flatten_dict(report)
        writer = csv.writer(output)
        writer.writerow(["Field", "Value"])
        for k, v in flat.items():
            writer.writerow([k, str(v)])
        return {"content": output.getvalue(), "filename": f"report_{report.get('month', 'monthly')}.csv"}

    def _to_pdf(self, report: Dict) -> Dict[str, Any]:
        """Convert report to PDF (placeholder - would use reportlab/weasyprint)."""
        # In production, use reportlab or weasyprint
        return {"content": "PDF generation not implemented", "filename": "report.pdf"}

    def _flatten_dict(self, d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)