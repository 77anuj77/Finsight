"""
Audit Repository
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import Session

from backend.app.models.audit import AuditLog


class AuditRepo:
    """Repository for AuditLog data access."""

    @staticmethod
    def create(db: Session, log_data: dict) -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(**log_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_filtered(
        db: Session,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get filtered audit logs."""
        query = select(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)

        query = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())