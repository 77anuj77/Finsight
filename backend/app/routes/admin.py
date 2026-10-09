"""
Admin Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user, require_role
from backend.app.repositories.user_repo import UserRepo
from backend.app.schemas.user import UserResponse, UserWithStats
from backend.app.models.user import User
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = Query(None, pattern="^(USER|ADMIN|SUPER_ADMIN)$"),
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=UserWithStats)
def get_user(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Get user with stats (admin only)."""
    user = UserRepo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRepo.get_with_stats(db, user_id)


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)."""
    user = UserRepo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    UserRepo.deactivate(db, user)
    return {"message": "User deactivated"}


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Activate a user (admin only)."""
    user = UserRepo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()
    return {"message": "User activated"}


@router.get("/analytics/aggregate")
def get_aggregate_analytics(
    month: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Get aggregate analytics across all users (admin only)."""
    return AnalyticsService.get_aggregate_analytics(db, month)


@router.get("/audit-logs")
def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)."""
    from backend.app.repositories.audit_repo import AuditRepo
    return AuditRepo.get_filtered(db, user_id, action, start_date, end_date, skip, limit)