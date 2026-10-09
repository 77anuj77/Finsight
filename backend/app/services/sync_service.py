"""
Sync Service - PostgreSQL to MongoDB synchronization
"""
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from backend.app.db.mongo import get_mongo_db
from backend.app.models.transaction import Transaction
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.category import Category


class SyncService:
    """Service for syncing PostgreSQL data to MongoDB for analytics."""

    def __init__(self):
        self.mongo_db = None

    def _get_db(self):
        """Lazy initialization of MongoDB connection."""
        if self.mongo_db is None:
            self.mongo_db = get_mongo_db()
        return self.mongo_db

    def sync_transaction(self, transaction: Transaction) -> None:
        """Sync a transaction to MongoDB (denormalized)."""
        db = self._get_db()
        if db is None:
            return

        # Get related data for denormalization
        # In production, these would be passed in or cached
        doc = {
            "tx_id": str(transaction.id),
            "user_id": str(transaction.user_id),
            "account_id": str(transaction.account_id),
            "type": transaction.type,
            "amount": float(transaction.amount),
            "category_id": transaction.category_id,
            "payee": transaction.payee,
            "transacted_at": transaction.transacted_at.isoformat() if hasattr(transaction.transacted_at, 'isoformat') else str(transaction.transacted_at),
            "month_key": self._get_month_key(transaction.transacted_at),
            "notes": transaction.notes,
            "flag_status": transaction.flag_status,
            "source": transaction.source,
            "receipt_ref": transaction.receipt_ref,
            "created_at": datetime.utcnow(),
            "features": self._compute_features(transaction),
        }

        # Upsert (idempotent)
        db.txn_analytics.update_one(
            {"tx_id": str(transaction.id)},
            {"$set": doc},
            upsert=True
        )

    def delete_transaction(self, tx_id: str) -> None:
        """Delete a transaction from MongoDB."""
        db = self._get_db()
        if db is None:
            return

        db.txn_analytics.delete_one({"tx_id": tx_id})

    def sync_user(self, user: User) -> None:
        """Sync user profile to MongoDB."""
        db = self._get_db()
        if db is None:
            return

        doc = {
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "currency": user.currency,
            "monthly_income": float(user.monthly_income),
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else str(user.created_at),
            "updated_at": datetime.utcnow(),
        }

        db.users.update_one(
            {"user_id": str(user.id)},
            {"$set": doc},
            upsert=True
        )

    def sync_account(self, account: Account) -> None:
        """Sync account to MongoDB."""
        db = self._get_db()
        if db is None:
            return

        doc = {
            "account_id": str(account.id),
            "user_id": str(account.user_id),
            "name": account.name,
            "type": account.type,
            "balance": float(account.balance),
            "currency": account.currency,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat() if hasattr(account.created_at, 'isoformat') else str(account.created_at),
            "updated_at": datetime.utcnow(),
        }

        db.accounts.update_one(
            {"account_id": str(account.id)},
            {"$set": doc},
            upsert=True
        )

    def _get_month_key(self, dt) -> str:
        """Get month key in YYYY-MM format."""
        if hasattr(dt, 'strftime'):
            return dt.strftime("%Y-%m")
        try:
            parsed = datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
            return parsed.strftime("%Y-%m")
        except:
            return datetime.utcnow().strftime("%Y-%m")

    def _compute_features(self, transaction: Transaction) -> Dict[str, Any]:
        """Compute ML features for a transaction."""
        # These would be computed from user history in production
        return {
            "amount_z": 0.0,
            "is_weekend": self._is_weekend(transaction.transacted_at),
            "hour_of_day": self._get_hour(transaction.transacted_at),
            "days_since_last_txn": 0,
            "is_new_payee": False,
        }

    def _is_weekend(self, dt) -> bool:
        if hasattr(dt, 'weekday'):
            return dt.weekday() >= 5
        try:
            parsed = datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
            return parsed.weekday() >= 5
        except:
            return False

    def _get_hour(self, dt) -> int:
        if hasattr(dt, 'hour'):
            return dt.hour
        try:
            parsed = datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
            return parsed.hour
        except:
            return 12

    def reconcile(self, user_id: str) -> Dict[str, int]:
        """Reconcile PostgreSQL and MongoDB data for a user."""
        # This would compare counts and fix discrepancies
        # Placeholder for now
        return {"synced": 0, "errors": 0}