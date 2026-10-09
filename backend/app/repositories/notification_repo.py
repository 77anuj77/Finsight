"""
Notification Repository
"""
from typing import List, Optional
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import Session

from backend.app.models.notification import Notification


class NotificationRepo:
    """Repository for Notification data access."""

    @staticmethod
    def get_by_id(db: Session, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        result = db.execute(select(Notification).where(Notification.id == notification_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_user(db: Session, user_id: str, unread_only: bool = False,
                   limit: int = 50) -> List[Notification]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
        query = query.order_by(desc(Notification.created_at)).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def create(db: Session, notification_data: dict) -> Notification:
        """Create a new notification."""
        notification = Notification(**notification_data)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_read(db: Session, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        from sqlalchemy import update
        result = db.execute(
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.is_read == False))
            .values(is_read=True)
        )
        db.commit()
        return result.rowcount