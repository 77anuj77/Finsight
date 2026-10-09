"""
Savings Goals Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from backend.app.db.postgres import get_db
from backend.app.core.deps import get_current_user
from backend.app.repositories.goal_repo import GoalRepo
from backend.app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, GoalWithProgress
from backend.app.models.user import User

router = APIRouter(prefix="/api/goals", tags=["Goals"])


@router.get("/", response_model=List[GoalResponse])
def list_goals(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all savings goals for the current user."""
    return GoalRepo.get_by_user(db, current_user.id, status)


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new savings goal."""
    goal = GoalRepo.create(db, {
        **goal_data.model_dump(),
        "user_id": current_user.id,
        "current_amount": Decimal('0.00'),
        "status": "ACTIVE",
    })
    return goal


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific savings goal."""
    goal = GoalRepo.get_by_id(db, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a savings goal."""
    goal = GoalRepo.get_by_id(db, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    updates = goal_data.model_dump(exclude_unset=True)
    return GoalRepo.update(db, goal, updates)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a savings goal."""
    goal = GoalRepo.get_by_id(db, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    GoalRepo.delete(db, goal)


@router.get("/{goal_id}/progress", response_model=GoalWithProgress)
def get_goal_progress(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal with progress calculation."""
    goal = GoalRepo.get_by_id(db, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    return GoalRepo.get_with_progress(db, goal_id)


@router.post("/{goal_id}/sweep", response_model=GoalResponse)
def trigger_sweep(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger auto-sweep for a goal."""
    goal = GoalRepo.get_by_id(db, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    return GoalRepo.trigger_sweep(db, goal)