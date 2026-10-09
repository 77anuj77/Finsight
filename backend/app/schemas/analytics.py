"""
Pydantic schemas for Analytics API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class DashboardStats(BaseModel):
    """Dashboard statistics response"""
    transaction_count: int
    income_this_month: float
    expense_this_month: float
    net_balance_this_month: float
    budget_count: int
    total_budget_limit: float
    avg_transaction_value: float
    total_net_worth: float
    total_accounts: int


class SpendingByCategory(BaseModel):
    """Spending by category"""
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
    percentage: float


class MonthlyTrend(BaseModel):
    """Monthly spending trend"""
    month: str
    income: float
    expense: float
    net: float


class TopPayees(BaseModel):
    """Top payees"""
    payee_name: str
    category_name: str
    category_id: int
    total_spent: float
    transaction_count: int
    category_utilization_pct: float


class BudgetHealth(BaseModel):
    """Budget health score"""
    score: int  # 0-100
    components: Dict[str, float]
    breakdown: Dict[str, Any]


class AnalyticsDashboard(BaseModel):
    """Full analytics dashboard response"""
    stats: DashboardStats
    spending_by_category: List[SpendingByCategory]
    monthly_trend: List[MonthlyTrend]
    top_payees: List[TopPayees]
    budget_health: BudgetHealth
    budget_vs_actual: List[dict]


class CategorySpending(BaseModel):
    """Category spending detail"""
    category_id: int
    category_name: str
    total: float
    count: int
    avg: float
    min: float
    max: float


class MonthlySummary(BaseModel):
    """Monthly financial summary"""
    month: str
    total_income: float
    total_expense: float
    net_savings: float
    transaction_count: int
    avg_daily_spend: float