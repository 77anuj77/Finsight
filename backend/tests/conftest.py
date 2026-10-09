"""
Pytest Configuration and Fixtures
"""
import pytest
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.db.postgres import SessionLocal, Base, engine, init_db, drop_db
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction as TransactionModel
from backend.app.models.budget import Budget
from backend.app.models.goal import SavingsGoal
from backend.app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Set up test database."""
    # Create all tables
    init_db()
    yield
    # Clean up
    drop_db()


@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        full_name="Test User",
        role="USER",
        currency="INR",
        monthly_income=12000.00,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        id="admin-user-id",
        email="admin@example.com",
        password_hash=get_password_hash("AdminPassword123!"),
        full_name="Admin User",
        role="ADMIN",
        currency="INR",
        monthly_income=50000.00,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_categories(db_session):
    """Create default categories."""
    categories = [
        Category(id=1, name="Income", kind="INCOME", is_default=True),
        Category(id=2, name="Food & Dining", kind="EXPENSE", is_default=True),
        Category(id=3, name="Transport", kind="EXPENSE", is_default=True),
        Category(id=4, name="Rent", kind="EXPENSE", is_default=True),
        Category(id=5, name="Education", kind="EXPENSE", is_default=True),
        Category(id=6, name="Subscriptions", kind="EXPENSE", is_default=True),
        Category(id=7, name="Shopping", kind="EXPENSE", is_default=True),
        Category(id=8, name="Entertainment", kind="EXPENSE", is_default=True),
        Category(id=9, name="Health", kind="EXPENSE", is_default=True),
        Category(id=10, name="Savings", kind="EXPENSE", is_default=True),
        Category(id=11, name="Other", kind="EXPENSE", is_default=True),
        Category(id=0, name="Transfer", kind="EXPENSE", is_default=True),
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    return categories


@pytest.fixture
def test_account(db_session, test_user):
    """Create a test account."""
    account = Account(
        id="test-account-id",
        user_id=test_user.id,
        name="Test Bank Account",
        type="BANK",
        balance=Decimal('10000.00'),
        currency="INR",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for test user."""
    token = create_access_token({"sub": test_user.id, "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin):
    """Generate auth headers for admin user."""
    token = create_access_token({"sub": test_admin.id, "role": test_admin.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_mongo():
    """Mock MongoDB for tests."""
    with patch('backend.app.db.mongo.get_mongo_db') as mock:
        mock_db = MagicMock()
        mock_db.txn_analytics = MagicMock()
        mock_db.users = MagicMock()
        mock_db.accounts = MagicMock()
        mock_db.ai_insights = MagicMock()
        mock.return_value = mock_db
        yield mock_db