"""
FastAPI Dependencies
"""
from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from backend.app.db.postgres import get_db
from backend.app.core.security import get_current_user, get_current_active_user
from backend.app.models.user import User


def get_current_active_user_dep(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role: str):
    """Dependency to enforce role-based access control."""
    def role_checker(current_user: User = Depends(get_current_active_user_dep)) -> User:
        if current_user.role != role and current_user.role != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing privileges for role: {role}"
            )
        return current_user
    return role_checker


# Convenience dependencies
def get_current_admin(current_user: User = Depends(require_role("ADMIN"))) -> User:
    return current_user

def get_current_super_admin(current_user: User = Depends(require_role("SUPER_ADMIN"))) -> User:
    return current_user