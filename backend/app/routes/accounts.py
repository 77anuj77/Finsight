"""
Accounts Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.repositories.account_repo import AccountRepo
from backend.app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from backend.app.models.user import User

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all accounts for the current user."""
    return AccountRepo.get_by_user(db, current_user.id)


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new account."""
    account = AccountRepo.create(db, {
        **account_data.model_dump(),
        "user_id": current_user.id,
        "balance": Decimal('0.00'),
        "is_active": True,
    })
    return account


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific account."""
    account = AccountRepo.get_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: str,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an account."""
    account = AccountRepo.get_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")

    updates = account_data.model_dump(exclude_unset=True)
    return AccountRepo.update(db, account, updates)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an account (soft delete - mark inactive)."""
    account = AccountRepo.get_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")

    AccountRepo.deactivate(db, account)