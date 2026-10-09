"""
Transaction Service - Business logic for transactions
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from typing import Optional

from backend.app.repositories.transaction_repo import TransactionRepo
from backend.app.repositories.account_repo import AccountRepo
from backend.app.repositories.category_repo import CategoryRepo
from backend.app.services.fraud_service import FraudService
from backend.app.services.categorization_service import CategorizationService
from backend.app.services.sync_service import SyncService
from backend.app.services.notification_service import NotificationService
from backend.app.models.transaction import Transaction
from backend.app.models.account import Account


class TransactionService:
    """Service layer for transaction operations."""

    def __init__(self, db: Session):
        self.db = db
        self.fraud_service = FraudService()
        self.categorization_service = CategorizationService()
        self.sync_service = SyncService()
        self.notification_service = NotificationService()

    def create_transaction(self, transaction_data: dict, user_id: str) -> Transaction:
        """Create a transaction with balance update and fraud detection."""
        account_id = transaction_data["account_id"]
        amount = Decimal(str(transaction_data["amount"]))
        txn_type = transaction_data["type"]

        # Verify account and get current balance
        account = AccountRepo.get_by_id(self.db, account_id)
        if not account:
            raise ValueError("Account not found")

        # Check balance for expenses/transfers out
        if txn_type in ("EXPENSE", "TRANSFER"):
            if account.balance < amount:
                raise ValueError("Insufficient balance")
            new_balance = account.balance - amount
        elif txn_type == "INCOME":
            new_balance = account.balance + amount
        else:
            raise ValueError(f"Invalid transaction type: {txn_type}")

        # Auto-categorize if not provided or category is "Other"
        if "category_id" not in transaction_data or transaction_data["category_id"] == 0:
            predicted_category = self.categorization_service.predict(
                transaction_data.get("payee", ""),
                transaction_data.get("notes", "")
            )
            transaction_data["category_id"] = predicted_category

        # Fraud detection
        risk_score = self.fraud_service.score_transaction(
            user_id=user_id,
            amount=amount,
            payee=transaction_data.get("payee"),
            category_id=transaction_data.get("category_id"),
            transacted_at=transaction_data.get("transacted_at", datetime.utcnow()),
            account_id=account_id,
        )

        flag_status = "NORMAL"
        if risk_score >= 0.7:
            flag_status = "SUSPICIOUS"
        elif risk_score >= 0.5:
            flag_status = "REVIEW"

        # Create transaction
        transaction = TransactionRepo.create(self.db, {
            **transaction_data,
            "user_id": user_id,
            "flag_status": flag_status,
            "source": "MANUAL",
        })

        # Update account balance
        AccountRepo.update_balance(self.db, account_id, new_balance)

        # Sync to MongoDB
        self.sync_service.sync_transaction(transaction)

        # Create notification if flagged
        if flag_status in ("SUSPICIOUS", "REVIEW"):
            self.notification_service.create_flag_notification(
                user_id, transaction.id, flag_status, risk_score
            )

        return transaction

    def update_transaction(self, transaction: Transaction, updates: dict) -> Transaction:
        """Update a transaction (with balance adjustment if amount changes)."""
        old_amount = Decimal(str(transaction.amount))
        new_amount = Decimal(str(updates.get("amount", old_amount)))
        amount_diff = new_amount - old_amount

        if amount_diff != 0:
            account = AccountRepo.get_by_id(self.db, transaction.account_id)
            if transaction.type in ("EXPENSE", "TRANSFER"):
                if account.balance < amount_diff:
                    raise ValueError("Insufficient balance for amount increase")
                new_balance = account.balance - amount_diff
            elif transaction.type == "INCOME":
                new_balance = account.balance + amount_diff

            AccountRepo.update_balance(self.db, account.id, new_balance)

        # Update transaction
        updated = TransactionRepo.update(self.db, transaction, updates)

        # Re-sync to MongoDB
        self.sync_service.sync_transaction(updated)

        return updated

    def delete_transaction(self, transaction: Transaction) -> None:
        """Delete a transaction and reverse balance impact."""
        account = AccountRepo.get_by_id(self.db, transaction.account_id)
        amount = Decimal(str(transaction.amount))

        # Reverse balance
        if transaction.type in ("EXPENSE", "TRANSFER"):
            new_balance = account.balance + amount
        elif transaction.type == "INCOME":
            new_balance = account.balance - amount

        AccountRepo.update_balance(self.db, account.id, new_balance)

        # Delete from MongoDB sync
        self.sync_service.delete_transaction(transaction.id)

        # Delete transaction
        TransactionRepo.delete(self.db, transaction)

    def confirm_flagged_transaction(self, transaction: Transaction, decision: str) -> Transaction:
        """Confirm or reject a flagged transaction."""
        if decision == "REJECTED":
            # Reverse the transaction
            self.delete_transaction(transaction)
            return transaction
        elif decision == "CONFIRMED":
            transaction.flag_status = "CONFIRMED"
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        else:
            raise ValueError("Invalid decision")

    def create_transfer(self, from_account_id: str, to_account_id: str,
                       amount: Decimal, user_id: str, notes: str = None) -> tuple:
        """Create a transfer between accounts."""
        from_account = AccountRepo.get_by_id(self.db, from_account_id)
        to_account = AccountRepo.get_by_id(self.db, to_account_id)

        if not from_account or not to_account:
            raise ValueError("One or both accounts not found")
        if from_account.user_id != user_id or to_account.user_id != user_id:
            raise ValueError("Account ownership mismatch")
        if from_account.balance < amount:
            raise ValueError("Insufficient balance")

        # Create outgoing transaction
        out_txn = TransactionRepo.create(self.db, {
            "account_id": from_account_id,
            "user_id": user_id,
            "category_id": 0,  # Transfer category
            "type": "TRANSFER",
            "amount": amount,
            "payee": f"Transfer to {to_account.name}",
            "transacted_at": datetime.utcnow(),
            "notes": notes,
            "flag_status": "NORMAL",
            "source": "MANUAL",
        })

        # Create incoming transaction
        in_txn = TransactionRepo.create(self.db, {
            "account_id": to_account_id,
            "user_id": user_id,
            "category_id": 0,
            "type": "TRANSFER",
            "amount": amount,
            "payee": f"Transfer from {from_account.name}",
            "transacted_at": datetime.utcnow(),
            "notes": notes,
            "flag_status": "NORMAL",
            "source": "MANUAL",
        })

        # Update balances
        AccountRepo.update_balance(self.db, from_account_id, from_account.balance - amount)
        AccountRepo.update_balance(self.db, to_account_id, to_account.balance + amount)

        # Sync both
        self.sync_service.sync_transaction(out_txn)
        self.sync_service.sync_transaction(in_txn)

        return out_txn, in_txn