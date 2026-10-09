"""
Transactions Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.repositories.transaction_repo import TransactionRepo
from backend.app.repositories.account_repo import AccountRepo
from backend.app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionList, TransactionConfirm, TransactionFilter
)
from backend.app.models.user import User

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("/", response_model=TransactionList)
def list_transactions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    category_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None, pattern="^(INCOME|EXPENSE|TRANSFER)$"),
    flag_status: Optional[str] = Query(None, pattern="^(NORMAL|SUSPICIOUS|REJECTED|CONFIRMED)$"),
    account_id: Optional[str] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List transactions with filters and pagination."""
    filters = TransactionFilter(
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        type=type,
        flag_status=flag_status,
        account_id=account_id,
        min_amount=min_amount,
        max_amount=max_amount,
        page=page,
        size=size
    )
    transactions, total = TransactionRepo.get_filtered(db, current_user.id, filters)

    pages = (total + size - 1) // size
    return TransactionList(
        items=transactions,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction."""
    # Verify account ownership
    account = AccountRepo.get_by_id(db, transaction_data.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")

    # Create transaction (service will handle balance update)
    transaction = TransactionRepo.create(db, {
        **transaction_data.model_dump(),
        "user_id": current_user.id,
        "flag_status": "NORMAL",
        "source": "MANUAL",
    })

    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction."""
    transaction = TransactionRepo.get_by_id(db, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction."""
    transaction = TransactionRepo.get_by_id(db, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = transaction_data.model_dump(exclude_unset=True)
    return TransactionRepo.update(db, transaction, updates)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    transaction = TransactionRepo.get_by_id(db, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    TransactionRepo.delete(db, transaction)


@router.post("/{transaction_id}/confirm", response_model=TransactionResponse)
def confirm_transaction(
    transaction_id: str,
    confirm_data: TransactionConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm or reject a flagged transaction."""
    transaction = TransactionRepo.get_by_id(db, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.flag_status not in ("SUSPICIOUS", "REJECTED"):
        raise HTTPException(status_code=400, detail="Transaction is not flagged")

    transaction.flag_status = confirm_data.decision
    db.commit()
    db.refresh(transaction)

    return transaction