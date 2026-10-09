"""
Analytics Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.services.analytics_service import AnalyticsService
from backend.app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard(
    month: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary for a month."""
    if month is None:
        month = date.today().replace(day=1)
    return AnalyticsService.get_dashboard(db, current_user.id, month)


@router.get("/trends")
def get_trends(
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly spending trends."""
    return AnalyticsService.get_trends(db, current_user.id, months)


@router.get("/category-breakdown")
def get_category_breakdown(
    month: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category."""
    if month is None:
        month = date.today().replace(day=1)
    return AnalyticsService.get_category_breakdown(db, current_user.id, month)


@router.get("/top-payees")
def get_top_payees(
    month: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top payees by total amount."""
    if month is None:
        month = date.today().replace(day=1)
    return AnalyticsService.get_top_payees(db, current_user.id, month, limit)


@router.get("/budget-vs-actual")
def get_budget_vs_actual(
    month: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget vs actual comparison."""
    if month is None:
        month = date.today().replace(day=1)
    return AnalyticsService.get_budget_vs_actual(db, current_user.id, month)


@router.get("/net-worth")
def get_net_worth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current net worth."""
    return AnalyticsService.get_net_worth(db, current_user.id)