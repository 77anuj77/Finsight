"""
Reports Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.services.reports_service import ReportsService
from backend.app.models.user import User

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/monthly")
def get_monthly_report(
    month: Optional[date] = Query(None),
    format: str = Query("json", pattern="^(json|csv|pdf)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly report in specified format."""
    if month is None:
        month = date.today().replace(day=1)
    return ReportsService.generate_monthly(db, current_user.id, month, format)


@router.get("/yearly")
def get_yearly_report(
    year: Optional[int] = Query(None),
    format: str = Query("json", pattern="^(json|csv|pdf)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get yearly report in specified format."""
    if year is None:
        year = date.today().year
    return ReportsService.generate_yearly(db, current_user.id, year, format)


@router.get("/transactions/export")
def export_transactions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", pattern="^(csv|json)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions for date range."""
    return ReportsService.export_transactions(db, current_user.id, start_date, end_date, format)