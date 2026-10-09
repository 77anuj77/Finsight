"""
Repository Pattern for Transaction Data Access
"""
from backend.app.db.postgres import get_db, Base
from backend.app.models.transaction import Transaction as TransactionModel
from typing import List, Optional, Tuple, TYPE_CHECKING
from sqlalchemy import select, and_, or_, func, cast, Numeric
from datetime import datetime, date

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.account import Account
    from backend.app.models.budget import Budget
    from backend.app.schemas.transaction import TransactionFilter


class TransactionRepo:
    """Repository for Transaction aggregates."""

    @staticmethod
    def get_by_id(db, transaction_id: str) -> Optional[TransactionModel]:
        """Get transaction by ID."""
        result = db.execute(
            select(TransactionModel).where(TransactionModel.id == transaction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def get_by_user(
        db,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        type: Optional[str] = None,
        category_id: Optional[int] = None,
        flag_status: Optional[str] = None
    ) -> List[TransactionModel]:
        """Get transactions for a user with optional filters."""
        query = select(TransactionModel).where(TransactionModel.user_id == user_id)

        if type:
            query = query.where(TransactionModel.type == type)
        if category_id:
            query = query.where(TransactionModel.category_id == category_id)
        if flag_status:
            query = query.where(TransactionModel.flag_status == flag_status)

        query = query.order_by(TransactionModel.transacted_at.desc())
        query = query.offset(skip).limit(limit)

        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_by_account(db, account_id: str, skip: int = 0, limit: int = 100) -> List[TransactionModel]:
        """Get all transactions for an account."""
        query = (
            select(TransactionModel)
            .where(TransactionModel.account_id == account_id)
            .order_by(TransactionModel.transacted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_filtered(db, user_id: str, filters: 'TransactionFilter') -> Tuple[List[TransactionModel], int]:
        """Get transactions with complex filters and pagination, returns (items, total_count)."""
        query = select(TransactionModel).where(TransactionModel.user_id == user_id)

        if filters.start_date:
            query = query.where(TransactionModel.transacted_at >= filters.start_date)
        if filters.end_date:
            query = query.where(TransactionModel.transacted_at <= filters.end_date)
        if filters.category_id:
            query = query.where(TransactionModel.category_id == filters.category_id)
        if filters.type:
            query = query.where(TransactionModel.type == filters.type)
        if filters.flag_status:
            query = query.where(TransactionModel.flag_status == filters.flag_status)
        if filters.account_id:
            query = query.where(TransactionModel.account_id == filters.account_id)
        if filters.min_amount:
            query = query.where(cast(TransactionModel.amount, Numeric(14, 2)) >= filters.min_amount)
        if filters.max_amount:
            query = query.where(cast(TransactionModel.amount, Numeric(14, 2)) <= filters.max_amount)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar() or 0

        # Apply pagination
        query = query.order_by(TransactionModel.transacted_at.desc())
        query = query.offset((filters.page - 1) * filters.size).limit(filters.size)

        result = db.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    def get_by_user_and_date_range(
        db, user_id: str, start_date: date, end_date: date
    ) -> List[TransactionModel]:
        """Get transactions for a user within a date range."""
        query = (
            select(TransactionModel)
            .where(
                TransactionModel.user_id == user_id,
                TransactionModel.transacted_at >= start_date,
                TransactionModel.transacted_at < end_date,
            )
            .order_by(TransactionModel.transacted_at.desc())
        )
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_by_category_and_date_range(
        db, user_id: str, category_id: int, start_date: date, end_date: date
    ) -> List[TransactionModel]:
        """Get transactions by category within a date range."""
        query = (
            select(TransactionModel)
            .where(
                TransactionModel.user_id == user_id,
                TransactionModel.category_id == category_id,
                TransactionModel.transacted_at >= start_date,
                TransactionModel.transacted_at < end_date,
            )
            .order_by(TransactionModel.transacted_at.desc())
        )
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_monthly_summary(db, user_id: str, month: str) -> dict:
        """
        Get monthly summary for a user.
        month format: 'YYYY-MM' (PG date_trunc('month', ...) returns this).
        """
        query = select(
            func.sum(cast(TransactionModel.amount, Numeric(14, 2))).filter(
                TransactionModel.type == 'EXPENSE',
                TransactionModel.user_id == user_id,
                TransactionModel.transacted_at >= f'{month}-01',
                TransactionModel.transacted_at < f'{month}-31'
            ).label('total_expense')
        )
        result = db.execute(query)
        total_expense = result.scalar() or 0

        income_query = select(
            func.sum(cast(TransactionModel.amount, Numeric(14, 2))).filter(
                TransactionModel.type == 'INCOME',
                TransactionModel.user_id == user_id,
                TransactionModel.transacted_at >= f'{month}-01',
                TransactionModel.transacted_at < f'{month}-31'
            ).label('total_income')
        )
        income_result = db.execute(income_query)
        total_income = income_result.scalar() or 0

        return {
            "user_id": user_id,
            "month": month,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_savings": float(total_income - total_expense),
        }

    @staticmethod
    def get_by_category(
        db,
        user_id: str,
        category_id: int,
        month: str
    ) -> List[TransactionModel]:
        """Get transactions by category for a specific month."""
        query = (
            select(TransactionModel)
            .where(
                TransactionModel.user_id == user_id,
                TransactionModel.category_id == category_id
            )
            .order_by(TransactionModel.transacted_at.desc())
        )
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def create(db, transaction_dict) -> TransactionModel:
        """Create a new transaction."""
        transaction = TransactionModel(**transaction_dict)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def update(db, transaction: TransactionModel, updates: dict) -> TransactionModel:
        """Update transaction fields."""
        for field, value in updates.items():
            setattr(transaction, field, value)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def delete(db, transaction: TransactionModel) -> None:
        """Delete a transaction."""
        db.delete(transaction)
        db.commit()

    @staticmethod
    def flag_transaction(db, transaction_id: str, flag_status: str) -> TransactionModel:
        """Update transaction flag status."""
        transaction = TransactionRepo.get_by_id(db, transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")
        transaction.flag_status = flag_status
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def reverse_transaction(db, transaction: TransactionModel, account_repo) -> None:
        """Reverse transaction (decrease income, increase expense/transaction)."""
        # Simplified version - real implementation would call stored procedure
        raise NotImplementedError("Use fn_reverse_transaction or TransactionService.reverse()")