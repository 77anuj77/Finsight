"""
Tests for Transaction Module
"""
import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

from backend.app.repositories.transaction_repo import TransactionRepo
from backend.app.models.transaction import Transaction as TransactionModel
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.category import Category
from backend.app.services.transaction_service import TransactionService
from backend.app.schemas.transaction import TransactionCreate, TransactionFilter


class TestTransactionRepo:
    """Test Transaction Repository."""

    def test_create_transaction(self, db_session, test_user, test_account, test_categories):
        """Test creating a transaction."""
        txn_data = {
            "account_id": test_account.id,
            "user_id": test_user.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('500.00'),
            "payee": "Test Restaurant",
            "transacted_at": datetime.utcnow(),
            "notes": "Test transaction",
            "flag_status": "NORMAL",
            "source": "MANUAL",
        }

        txn = TransactionRepo.create(db_session, txn_data)

        assert txn is not None
        assert txn.id is not None
        assert txn.amount == Decimal('500.00')
        assert txn.type == "EXPENSE"
        assert txn.payee == "Test Restaurant"

    def test_get_by_id(self, db_session, test_user, test_account, test_categories):
        """Test getting transaction by ID."""
        txn_data = {
            "account_id": test_account.id,
            "user_id": test_user.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('300.00'),
            "payee": "Another Restaurant",
            "transacted_at": datetime.utcnow(),
            "flag_status": "NORMAL",
            "source": "MANUAL",
        }
        created = TransactionRepo.create(db_session, txn_data)

        fetched = TransactionRepo.get_by_id(db_session, created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.amount == Decimal('300.00')

    def test_get_by_user(self, db_session, test_user, test_account, test_categories):
        """Test getting transactions by user."""
        # Create multiple transactions
        for i in range(3):
            txn_data = {
                "account_id": test_account.id,
                "user_id": test_user.id,
                "category_id": 2,
                "type": "EXPENSE",
                "amount": Decimal(f'{100 * (i+1)}.00'),
                "payee": f"Payee {i}",
                "transacted_at": datetime.utcnow() - timedelta(days=i),
                "flag_status": "NORMAL",
                "source": "MANUAL",
            }
            TransactionRepo.create(db_session, txn_data)

        transactions = TransactionRepo.get_by_user(db_session, test_user.id, limit=10)

        assert len(transactions) == 3
        assert all(t.user_id == test_user.id for t in transactions)

    def test_get_filtered(self, db_session, test_user, test_account, test_categories):
        """Test filtered transaction query."""
        # Create transactions with different properties
        now = datetime.utcnow()
        for i in range(5):
            txn_data = {
                "account_id": test_account.id,
                "user_id": test_user.id,
                "category_id": 2 if i < 3 else 3,
                "type": "EXPENSE" if i < 4 else "INCOME",
                "amount": Decimal(f'{100 * (i+1)}.00'),
                "payee": f"Payee {i}",
                "transacted_at": now - timedelta(days=i),
                "flag_status": "NORMAL",
                "source": "MANUAL",
            }
            TransactionRepo.create(db_session, txn_data)

        # Filter by category
        filters = TransactionFilter(category_id=2, page=1, size=10)
        transactions, total = TransactionRepo.get_filtered(db_session, test_user.id, filters)

        assert total == 3
        assert len(transactions) == 3
        assert all(t.category_id == 2 for t in transactions)

    def test_get_by_date_range(self, db_session, test_user, test_account, test_categories):
        """Test getting transactions by date range."""
        now = datetime.utcnow()
        start = date.today() - timedelta(days=30)
        end = date.today()

        for i in range(5):
            txn_data = {
                "account_id": test_account.id,
                "user_id": test_user.id,
                "category_id": 2,
                "type": "EXPENSE",
                "amount": Decimal('100.00'),
                "payee": f"Payee {i}",
                "transacted_at": now - timedelta(days=i*5),
                "flag_status": "NORMAL",
                "source": "MANUAL",
            }
            TransactionRepo.create(db_session, txn_data)

        transactions = TransactionRepo.get_by_user_and_date_range(
            db_session, test_user.id, start, end
        )

        assert len(transactions) == 5

    def test_update_transaction(self, db_session, test_user, test_account, test_categories):
        """Test updating a transaction."""
        txn_data = {
            "account_id": test_account.id,
            "user_id": test_user.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('200.00'),
            "payee": "Original Payee",
            "transacted_at": datetime.utcnow(),
            "flag_status": "NORMAL",
            "source": "MANUAL",
        }
        txn = TransactionRepo.create(db_session, txn_data)

        updated = TransactionRepo.update(db_session, txn, {"payee": "Updated Payee", "amount": Decimal('250.00')})

        assert updated.payee == "Updated Payee"
        assert updated.amount == Decimal('250.00')

    def test_delete_transaction(self, db_session, test_user, test_account, test_categories):
        """Test deleting a transaction."""
        txn_data = {
            "account_id": test_account.id,
            "user_id": test_user.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('150.00'),
            "payee": "To Delete",
            "transacted_at": datetime.utcnow(),
            "flag_status": "NORMAL",
            "source": "MANUAL",
        }
        txn = TransactionRepo.create(db_session, txn_data)

        TransactionRepo.delete(db_session, txn)

        deleted = TransactionRepo.get_by_id(db_session, txn.id)
        assert deleted is None


class TestTransactionService:
    """Test Transaction Service."""

    def test_create_expense_transaction(self, db_session, test_user, test_account, test_categories):
        """Test creating an expense transaction updates balance."""
        initial_balance = test_account.balance

        service = TransactionService(db_session)

        txn_data = {
            "account_id": test_account.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('500.00'),
            "payee": "Test Restaurant",
            "transacted_at": datetime.utcnow(),
            "notes": "Test expense",
        }

        txn = service.create_transaction(txn_data, test_user.id)

        # Check transaction created
        assert txn is not None
        assert txn.type == "EXPENSE"
        assert txn.amount == Decimal('500.00')

        # Check balance updated
        db_session.refresh(test_account)
        assert test_account.balance == initial_balance - Decimal('500.00')

    def test_create_income_transaction(self, db_session, test_user, test_account, test_categories):
        """Test creating an income transaction updates balance."""
        initial_balance = test_account.balance

        service = TransactionService(db_session)

        txn_data = {
            "account_id": test_account.id,
            "category_id": 1,  # Income
            "type": "INCOME",
            "amount": Decimal('1000.00'),
            "payee": "Salary",
            "transacted_at": datetime.utcnow(),
            "notes": "Test income",
        }

        txn = service.create_transaction(txn_data, test_user.id)

        # Check transaction created
        assert txn is not None
        assert txn.type == "INCOME"

        # Check balance updated
        db_session.refresh(test_account)
        assert test_account.balance == initial_balance + Decimal('1000.00')

    def test_insufficient_balance_raises_error(self, db_session, test_user, test_account, test_categories):
        """Test that expense exceeding balance raises error."""
        service = TransactionService(db_session)

        txn_data = {
            "account_id": test_account.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('999999.00'),  # More than balance
            "payee": "Expensive Item",
            "transacted_at": datetime.utcnow(),
        }

        with pytest.raises(ValueError, match="Insufficient balance"):
            service.create_transaction(txn_data, test_user.id)

    def test_create_transfer(self, db_session, test_user, test_account, test_categories):
        """Test creating a transfer between accounts."""
        # Create second account
        account2 = Account(
            id="test-account-id-2",
            user_id=test_user.id,
            name="Test UPI Account",
            type="UPI",
            balance=Decimal('5000.00'),
            currency="INR",
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db_session.add(account2)
        db_session.commit()

        service = TransactionService(db_session)

        out_txn, in_txn = service.create_transfer(
            from_account_id=test_account.id,
            to_account_id=account2.id,
            amount=Decimal('1000.00'),
            user_id=test_user.id,
            notes="Test transfer"
        )

        assert out_txn.type == "TRANSFER"
        assert in_txn.type == "TRANSFER"
        assert out_txn.amount == Decimal('1000.00')
        assert in_txn.amount == Decimal('1000.00')

        # Check balances
        db_session.refresh(test_account)
        db_session.refresh(account2)
        assert test_account.balance == Decimal('9000.00')  # 10000 - 1000
        assert account2.balance == Decimal('6000.00')  # 5000 + 1000


class TestTransactionSchemas:
    """Test Transaction Pydantic Schemas."""

    def test_transaction_create_valid(self):
        """Test valid transaction creation schema."""
        data = {
            "account_id": "test-account-id",
            "category_id": 2,
            "type": "EXPENSE",
            "amount": "500.00",
            "payee": "Test Restaurant",
            "transacted_at": datetime.utcnow().isoformat(),
            "notes": "Test",
        }
        txn = TransactionCreate(**data)

        assert txn.amount == Decimal('500.00')
        assert txn.type == "EXPENSE"

    def test_transaction_create_invalid_amount(self):
        """Test invalid amount raises validation error."""
        data = {
            "account_id": "test-account-id",
            "category_id": 2,
            "type": "EXPENSE",
            "amount": "-100.00",  # Negative
            "transacted_at": datetime.utcnow().isoformat(),
        }

        with pytest.raises(ValueError):
            TransactionCreate(**data)

    def test_transaction_filter_defaults(self):
        """Test transaction filter default values."""
        filt = TransactionFilter()

        assert filt.page == 1
        assert filt.size == 20
        assert filt.start_date is None
        assert filt.end_date is None