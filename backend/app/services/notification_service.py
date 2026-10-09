"""
Notification Service - In-app notifications and alerts
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from backend.app.models.notification import Notification
from backend.app.repositories.notification_repo import NotificationRepo


class NotificationService:
    """Service for managing notifications."""

    def __init__(self, db: Session = None):
        self.db = db

    def create_notification(self, user_id: str, title: str, message: str,
                           type: str = "info", reference_id: str = None,
                           reference_type: str = None) -> Notification:
        """Create a new notification."""
        if self.db is None:
            return None

        return NotificationRepo.create(self.db, {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,  # info, warning, error, success
            "reference_id": reference_id,
            "reference_type": reference_type,
            "is_read": False,
            "created_at": datetime.utcnow(),
        })

    def create_flag_notification(self, user_id: str, transaction_id: str,
                                flag_status: str, risk_score: float) -> Notification:
        """Create notification for flagged transaction."""
        severity = "high" if flag_status == "SUSPICIOUS" else "medium"
        title = f"Transaction Flagged: {flag_status}"
        message = (f"A transaction has been flagged as {flag_status} with risk score {risk_score:.2f}. "
                  f"Please review and confirm or reject.")

        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            type="warning",
            reference_id=transaction_id,
            reference_type="transaction_flag",
        )

    def create_budget_alert(self, user_id: str, budget_id: str,
                           utilization: dict) -> Notification:
        """Create notification for budget breach alert."""
        title = "Budget Breach Warning"
        message = (f"Your budget for category {utilization.get('category_id')} "
                  f"is projected to be exceeded. Current utilization: "
                  f"{utilization.get('utilization_percentage', 0):.1f}%. "
                  f"Projected end-of-month: {utilization.get('projected_end_amount', 0):.2f}")

        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            type="warning",
            reference_id=budget_id,
            reference_type="budget_alert",
        )

    def create_goal_achieved(self, user_id: str, goal_id: str,
                            goal_name: str) -> Notification:
        """Create notification for goal achievement."""
        return self.create_notification(
            user_id=user_id,
            title="Goal Achieved!",
            message=f"Congratulations! You've reached your savings goal: {goal_name}",
            type="success",
            reference_id=goal_id,
            reference_type="goal_achieved",
        )

    def create_insight_ready(self, user_id: str, month: str) -> Notification:
        """Create notification for monthly insight readiness."""
        return self.create_notification(
            user_id=user_id,
            title="Monthly Insight Ready",
            message=f"Your AI-generated financial insight for {month} is now available.",
            type="info",
            reference_id=month,
            reference_type="insight_ready",
        )

    def get_user_notifications(self, user_id: str, unread_only: bool = False,
                              limit: int = 50) -> List[Notification]:
        """Get notifications for a user."""
        if self.db is None:
            return []
        return NotificationRepo.get_by_user(self.db, user_id, unread_only, limit)

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read."""
        if self.db is None:
            return False
        notification = NotificationRepo.get_by_id(self.db, notification_id)
        if notification and notification.user_id == user_id:
            notification.is_read = True
            self.db.commit()
            return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        if self.db is None:
            return 0
        return NotificationRepo.mark_all_read(self.db, user_id)