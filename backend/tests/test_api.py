"""
Tests for API Endpoints
"""
import pytest
from decimal import Decimal
from datetime import date, datetime
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.postgres import SessionLocal
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction as TransactionModel
from backend.app.core.security import get_password_hash, create_access_token


client = TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    user = User(
        id="api-test-user",
        email="api@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        full_name="API Test User",
        role="USER",
        currency="INR",
        monthly_income=15000.00,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_account(db_session, test_user):
    account = Account(
        id="api-test-account",
        user_id=test_user.id,
        name="API Test Bank",
        type="BANK",
        balance=Decimal('20000.00'),
        currency="INR",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def test_categories(db_session):
    categories = [
        Category(id=1, name="Income", kind="INCOME", is_default=True),
        Category(id=2, name="Food & Dining", kind="EXPENSE", is_default=True),
        Category(id=3, name="Transport", kind="EXPENSE", is_default=True),
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    return categories


@pytest.fixture
def auth_token(test_user):
    """Generate auth token for test user."""
    return create_access_token({"sub": test_user.id, "role": test_user.role})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register(self):
        """Test user registration."""
        response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "full_name": "New User"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data

    def test_register_duplicate_email(self, test_user):
        """Test registration with duplicate email fails."""
        response = client.post("/api/auth/register", json={
            "email": test_user.email,
            "password": "Password123!",
            "full_name": "Another User"
        })

        assert response.status_code == 409

    def test_login(self, test_user):
        """Test user login."""
        response = client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "TestPassword123!"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, test_user):
        """Test login with wrong password fails."""
        response = client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "WrongPassword"
        })

        assert response.status_code == 401

    def test_refresh_token(self, test_user):
        """Test token refresh."""
        # First login to get refresh token
        login_resp = client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "TestPassword123!"
        })
        refresh_token = login_resp.json()["refresh_token"]

        # Use refresh token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestAccountEndpoints:
    """Test account endpoints."""

    def test_list_accounts(self, auth_headers):
        """Test listing accounts."""
        response = client.get("/api/accounts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_account(self, auth_headers):
        """Test creating an account."""
        response = client.post("/api/accounts", headers=auth_headers, json={
            "name": "New Account",
            "type": "UPI",
            "currency": "INR"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Account"
        assert data["type"] == "UPI"
        assert data["balance"] == "0.00"

    def test_get_account(self, auth_headers, test_account):
        """Test getting a specific account."""
        response = client.get(f"/api/accounts/{test_account.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_account.id
        assert data["name"] == test_account.name

    def test_update_account(self, auth_headers, test_account):
        """Test updating an account."""
        response = client.put(f"/api/accounts/{test_account.id}", headers=auth_headers, json={
            "name": "Updated Name"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_delete_account(self, auth_headers, test_account):
        """Test deleting (deactivating) an account."""
        response = client.delete(f"/api/accounts/{test_account.id}", headers=auth_headers)

        assert response.status_code == 204


class TestTransactionEndpoints:
    """Test transaction endpoints."""

    def test_list_transactions(self, auth_headers, test_user, test_account, test_categories):
        """Test listing transactions."""
        # Create a transaction first
        txn = TransactionModel(
            id="api-test-txn",
            account_id=test_account.id,
            user_id=test_user.id,
            category_id=2,
            type="EXPENSE",
            amount=Decimal('250.00'),
            payee="API Test Restaurant",
            transacted_at=datetime.utcnow(),
            flag_status="NORMAL",
            source="MANUAL",
            created_at=datetime.utcnow(),
        )
        db = SessionLocal()
        db.add(txn)
        db.commit()
        db.close()

        response = client.get("/api/transactions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_create_transaction(self, auth_headers, test_account):
        """Test creating a transaction."""
        response = client.post("/api/transactions", headers=auth_headers, json={
            "account_id": test_account.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": "300.00",
            "payee": "New Restaurant",
            "transacted_at": datetime.utcnow().isoformat(),
            "notes": "Test transaction"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == "300.00"
        assert data["type"] == "EXPENSE"
        assert data["payee"] == "New Restaurant"

    def test_create_transaction_insufficient_balance(self, auth_headers, test_account):
        """Test creating transaction with insufficient balance fails."""
        response = client.post("/api/transactions", headers=auth_headers, json={
            "account_id": test_account.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": "999999.00",
            "payee": "Expensive",
            "transacted_at": datetime.utcnow().isoformat(),
        })

        assert response.status_code == 400

    def test_get_transaction(self, auth_headers, test_user, test_account, test_categories):
        """Test getting a specific transaction."""
        db = SessionLocal()
        txn = TransactionModel(
            id="api-get-txn",
            account_id=test_account.id,
            user_id=test_user.id,
            category_id=2,
            type="EXPENSE",
            amount=Decimal('150.00'),
            payee="Get Test",
            transacted_at=datetime.utcnow(),
            flag_status="NORMAL",
            source="MANUAL",
            created_at=datetime.utcnow(),
        )
        db.add(txn)
        db.commit()
        db.close()

        response = client.get(f"/api/transactions/{txn.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == txn.id
        assert data["amount"] == "150.00"

    def test_update_transaction(self, auth_headers, test_user, test_account, test_categories):
        """Test updating a transaction."""
        db = SessionLocal()
        txn = TransactionModel(
            id="api-update-txn",
            account_id=test_account.id,
            user_id=test_user.id,
            category_id=2,
            type="EXPENSE",
            amount=Decimal('200.00'),
            payee="Original",
            transacted_at=datetime.utcnow(),
            flag_status="NORMAL",
            source="MANUAL",
            created_at=datetime.utcnow(),
        )
        db.add(txn)
        db.commit()
        db.close()

        response = client.put(f"/api/transactions/{txn.id}", headers=auth_headers, json={
            "payee": "Updated",
            "amount": "250.00"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["payee"] == "Updated"
        assert data["amount"] == "250.00"


class TestBudgetEndpoints:
    """Test budget endpoints."""

    def test_list_budgets(self, auth_headers, test_user, test_categories):
        """Test listing budgets."""
        response = client.get("/api/budgets", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_budget(self, auth_headers):
        """Test creating a budget."""
        month = date.today().replace(day=1).isoformat()
        response = client.post("/api/budgets", headers=auth_headers, json={
            "category_id": 2,
            "month": month,
            "limit_amount": "3000.00"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["category_id"] == 2
        assert data["limit_amount"] == "3000.00"

    def test_get_budget_utilization(self, auth_headers, test_user, test_categories):
        """Test getting budget utilization."""
        month = date.today().replace(day=1)
        db = SessionLocal()
        budget = Budget(
            id="api-budget-util",
            user_id=test_user.id,
            category_id=2,
            month=month,
            limit_amount=Decimal('2000.00'),
            created_at=datetime.utcnow(),
        )
        db.add(budget)
        db.commit()
        db.close()

        response = client.get(f"/api/budgets/{budget.id}/utilization", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["budget_id"] == budget.id


class TestGoalEndpoints:
    """Test savings goal endpoints."""

    def test_list_goals(self, auth_headers):
        """Test listing goals."""
        response = client.get("/api/goals", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_goal(self, auth_headers):
        """Test creating a savings goal."""
        response = client.post("/api/goals", headers=auth_headers, json={
            "name": "Emergency Fund",
            "target_amount": "50000.00",
            "auto_sweep_pct": 10.0,
            "deadline": (date.today().replace(day=1) + __import__('datetime').timedelta(days=180)).isoformat()
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Emergency Fund"
        assert data["target_amount"] == "50000.00"
        assert data["auto_sweep_pct"] == 10.0


class TestAnalyticsEndpoints:
    """Test analytics endpoints."""

    def test_dashboard(self, auth_headers, test_user, test_account):
        """Test dashboard endpoint."""
        response = client.get("/api/analytics/dashboard", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "net_savings" in data
        assert "total_balance" in data

    def test_trends(self, auth_headers):
        """Test trends endpoint."""
        response = client.get("/api/analytics/trends", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_category_breakdown(self, auth_headers):
        """Test category breakdown endpoint."""
        response = client.get("/api/analytics/category-breakdown", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_net_worth(self, auth_headers, test_account):
        """Test net worth endpoint."""
        response = client.get("/api/analytics/net-worth", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_net_worth" in data
        assert "accounts" in data


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test health check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "FinSight"