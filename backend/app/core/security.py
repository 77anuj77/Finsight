"""
Security Utilities
Handles JWT tokens, password hashing with bcrypt, and token rotation.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.db.postgres import get_db, SessionLocal
from backend.app.models.user import User
from backend.app.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

# bcrypt password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token() -> str:
    """Generate a new refresh token."""
    import uuid
    return str(uuid.uuid4())


def create_tokens(user: User) -> Dict[str, str]:
    """Create both access and refresh tokens for a user."""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "type": "access"
    }
    access_token = create_access_token(payload)

    payload["type"] = "refresh"
    refresh_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT and return payload."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Repository layer dependency to get current authenticated user.
    Validates token and returns User from DB.
    """
    from backend.app.repositories.user_repo import UserRepo
    from backend.app.core.exceptions import UnauthorizedException

    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token")

    user = UserRepo.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_role(role: str):
    """
    Dependency to enforce role-based access control.
    Usage: @router.get("/admin", dependencies=[Depends(require_role("ADMIN"))])
    """
    from backend.app.core.exceptions import ForbiddenException
    from backend.app.core.deps import current_user

    user = await current_user
    if user.role != role:
        raise ForbiddenException(f"Missing privileges for role: {role}")
    return user