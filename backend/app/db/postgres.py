"""
PostgreSQL Database Connection for FinSight
SQLAlchemy 2.0 Core + ORM with async support
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
from typing import Generator

from backend.app.config import settings


# Declarative base for SQLAlchemy 2.0 models
class Base(DeclarativeBase):
    pass


# Create sync engine (use NullPool for testing, QueuePool for production)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator:
    """
    FastAPI dependency for database session.
    Yields a session with expire_on_commit=False.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables (for development/testing)."""
    # Import all models to register them
    from backend.app.models import user, account, category, transaction, budget, goal, transfer, audit, notification  # noqa
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all tables (for testing)."""
    from backend.app.models import user, account, category, transaction, budget, goal, transfer, audit, notification  # noqa
    Base.metadata.drop_all(bind=engine)