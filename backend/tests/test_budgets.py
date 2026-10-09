"""
Tests for Budget Module
"""
import pytest
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from backend.app.repositories.budget_repo import BudgetRepo
from backend.app.models.budget import Budget
from backend.app.models.user import User
from backend.app.services.budget_service import BudgetService
from backend.app.schemas.budget import BudgetCreate


class TestBudgetRepo:
    """Test Budget Repository."""

    def test_create_budget(self, db_session, test_user, test_categories):
        """Test creating a budget."""
        budget_data = {
            "user_id": test_user.id,
            "category_id": 2,
            "month": date.today().replace(day=1),
            "limit_amount": Decimal('3000.00'),
        }

        budget = BudgetRepo.create(db_session, budget_data)

        assert budget is not None
        assert budget.id is not None
        assert budget.limit_amount == Decimal('3000.00')
        assert budget.user_id == test_user.id

    def test_get_by_id(self, db_session, test_user, test_categories):
        """Test getting budget by ID."""
        budget_data = {
            "user_id": test_user.id,
            "category_id": 2,
            "month": date.today().replace(day=1),
            "limit_amount": Decimal('2000.00'),
        }
        created = BudgetRepo.create(db_session, budget_data)

        fetched = BudgetRepo.get_by_id(db_session, created.id)

        assert fetched is not None
        assert fetched.id == created.id

    def test_get_by_user_and_month(self, db_session, test_user, test_categories):
        """Test getting budgets for user and month."""
        month = date.today().replace(day=1)

        for cat_id in [2, 3, 4]:
            budget_data = {
                "user_id": test_user.id,
                "category_id": cat_id,
                "month": month,
                "limit_amount": Decimal('1000.00'),
            }
            BudgetRepo.create(db_session, budget_data)

        budgets = BudgetRepo.get_by_user_and_month(db_session, test_user.id, month)

        assert len(budgets) == 3

    def test_get_by_category(self, db_session, test_user, test_categories):
        """Test getting budget by category."""
        month = date.today().replace(day=1)

        budget_data = {
            "user_id": test_user.id,
            "category_id": 2,
            "month": month,
            "limit_amount": Decimal('1500.00'),
        }
        BudgetRepo.create(db_session, budget_data)

        budget = BudgetRepo.get_by_category(db_session, test_user.id, 2, month)

        assert budget is not None
        assert budget.category_id == 2


class TestBudgetService:
    """Test Budget Service."""

    def test_get_budget_utilization(self, db_session, test_user, test_account, test_categories):
        """Test budget utilization calculation."""
        month = date.today().replace(day=1)

        # Create budget
        budget = BudgetRepo.create(db_session, {
            "user_id": test_user.id,
            "category_id": 2,
            "month": month,
            "limit_amount": Decimal('3000.00'),
        })

        # Create transactions for this category
        for i in range(3):
            txn = TransactionModel(
                id=f"txn-{i}",
                account_id=test_account.id,
                user_id=test_user.id,
                category_id=2,
                type="EXPENSE",
                amount=Decimal('500.00'),
                payee=f"Restaurant {i}",
                transacted_at=datetime.utcnow() - datetime.timedelta(days=i*5),
                flag_status="NORMAL",
                source="MANUAL",
                created_at=datetime.utcnow(),
            )
            db_session.add(txn)
        db_session.commit()

        service = BudgetService(db_session)
        utilization = service.get_budget_utilization(budget.id)

        assert utilization is not None
        assert utilization["limit_amount"] == Decimal('3000.00')
        assert utilization["spent_amount"] == Decimal('1500.00')
        assert utilization["utilization_percentage"] == 50.0

    def test_check_all_budgets(self, db_session, test_user, test_account, test_categories):
        """Test budget breach checking."""
        month = date.today().replace(day=1)

        # Create budget
        budget = BudgetRepo.create(db_session, {
            "user_id": test_user.id,
            "category_id": 2,
            "month": month,
            "limit_amount": Decimal('1000.00'),
        })

        # Create transactions exceeding budget
        for i in range(5):
            txn = TransactionModel(
                id=f"txn-{i}",
                account_id=test_account.id,
                user_id=test_user.id,
                category_id=2,
                type="EXPENSE",
                amount=Decimal('300.00'),  # Total 1500 > 1000 limit
                payee=f"Restaurant {i}",
                transacted_at=datetime.utcnow() - datetime.timedelta(days=i*5),
                flag_status="NORMAL",
                source="MANUAL",
                created_at=datetime.utcnow(),
            )
            db_session.add(txn)
        db_session.commit()

        service = BudgetService(db_session)
        alerts = service.check_all_budgets(test_user.id)

        assert len(alerts) > 0
        assert alerts[0]["budget_id"] == budget.id


class TestBudgetSchemas:
    """Test Budget Pydantic Schemas."""

    def test_budget_create_valid(self):
        """Test valid budget creation schema."""
        data = {
            "category_id": 2,
            "month": date.today().replace(day=1).isoformat(),
            "limit_amount": "3000.00",
        }
        budget = BudgetCreate(**data)

        assert budget.category_id == 2
        assert budget.limit_amount == Decimal('3000.00')

    def test_budget_create_invalid_amount(self):
        """Test invalid amount raises error."""
        data = {
            "category_id": 2,
            "month": date.today().replace(day=1).isoformat(),
            "limit_amount": "-100.00",
        }

        with pytest.raises(ValueError):
            BudgetCreate(**data)