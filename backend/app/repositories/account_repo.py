"""
Repository Pattern for Account Data Access
"""
from backend.app.db.postgres import get_db, Base
from backend.app.models.account import Account
from backend.app.models.transaction import Transaction as TransactionModel
from backend.app.models.transfer import Transfer
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import select, and_, or_

if TYPE_CHECKING:
    from backend.app.models.user import User


class AccountRepo:
    """Repository for Account aggregates."""

    @staticmethod
    def get_by_id(db, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        result = db.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_user(db, user_id: str, active_only: bool = True) -> List[Account]:
        """Get all accounts for a user, optionally filter active only."""
        query = select(Account).where(Account.user_id == user_id)
        if active_only:
            query = query.where(Account.is_active == True)
        query = query.order_by(Account.created_at.desc())
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def create(db, account_dict) -> Account:
        """Create a new account."""
        account = Account(**account_dict)
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def update(db, account: Account, updates: dict) -> Account:
        """Update account fields."""
        for field, value in updates.items():
            setattr(account, field, value)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db, account: Account) -> None:
        """Soft delete account (set is_active = False)."""
        account.is_active = False
        db.commit()

    @staticmethod
    def get_balance(db, account_id: str) -> float:
        """Get current balance (no lock needed for read)."""
        account = AccountRepo.get_by_id(db, account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        return float(account.balance)

    @staticmethod
    def check_balance(db, account_id: str, amount: float) -> bool:
        """Check if account has sufficient balance."""
        try:
            current_balance = AccountRepo.get_balance(db, account_id)
            return current_balance >= amount
        except Exception:
            return False

    @staticmethod
    def update_balance(db, account: Account, new_balance: float) -> Account:
        """Update account balance atomically."""
        account.balance = new_balance
        db.commit()
        db.refresh(account)
        return account