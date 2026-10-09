"""
AI Insights Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.services.insights_service import InsightsService
from backend.app.models.user import User

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/latest")
def get_latest_insight(
    month: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the latest AI-generated monthly insight."""
    if month is None:
        month = date.today().replace(day=1)
    return InsightsService.get_latest(db, current_user.id, month)


@router.post("/generate")
def generate_insight(
    month: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger insight generation for a month."""
    if month is None:
        month = date.today().replace(day=1)
    return InsightsService.generate(db, current_user.id, month)


@router.get("/history")
def get_insights_history(
    limit: int = Query(12, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of generated insights."""
    return InsightsService.get_history(db, current_user.id, limit)