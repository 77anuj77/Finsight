"""
Repository Pattern for User Data Access
"""
from backend.app.db.postgres import get_db, Base
from backend.app.models.user import User
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import select, and_, or_

if TYPE_CHECKING:
    from backend.app.models.account import Account
    from backend.app.models.transaction import Transaction as TransactionModel
    from backend.app.models.budget import Budget
    from backend.app.models.goal import SavingsGoal
    from backend.app.models.audit import AuditLog


class UserRepo:
    """Repository for User aggregates."""

    @staticmethod
    def get_by_email(db, email: str) -> Optional[User]:
        """Get user by email (unique lookups)."""
        result = db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_id(db, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_role(db, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with a given role (for admin)."""
        if role not in ("USER", "ADMIN", "SUPER_ADMIN"):
            raise ValueError(f"Invalid role: {role}")
        result = db.execute(
            select(User)
            .where(User.role == role)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    def get_active_users(db) -> List[User]:
        """Get all active users (for analytics)."""
        result = db.execute(
            select(User)
            .where(User.is_active == True)
            .order_by(User.created_at.desc())
            .limit(1000)
        )
        return list(result.scalars().all())

    @staticmethod
    def create(db, user_dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db, user: User, updates: dict) -> User:
        """Update user fields."""
        for field, value in updates.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate(db, user: User) -> User:
        """Soft deactivate user."""
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def password_change(db, user: User, new_hash: str) -> None:
        """Update password hash."""
        user.password_hash = new_hash
        db.commit()