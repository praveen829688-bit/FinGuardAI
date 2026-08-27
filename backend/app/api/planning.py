from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.goal_budget_service import (
    goal_budget_service
)


router = APIRouter(
    prefix="/api/planning",
    tags=["Financial Goals & Budgets"]
)


class GoalCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    description: str | None = None

    target_amount: float = Field(
        gt=0
    )

    target_date: datetime | None = None


class GoalContribution(BaseModel):
    amount: float = Field(
        gt=0
    )


class BudgetCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    amount: float = Field(
        gt=0
    )

    category_id: int | None = None

    period: str = Field(
        default="MONTHLY",
        min_length=3,
        max_length=30
    )


# ============================================================
# GOALS
# ============================================================

@router.post(
    "/goals",
    status_code=status.HTTP_201_CREATED
)
def create_goal(
    data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return goal_budget_service.create_goal(
        db=db,
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        target_amount=data.target_amount,
        target_date=data.target_date
    )


@router.get("/goals")
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "goals": goal_budget_service.get_goals(
            db,
            current_user.id
        )
    }


@router.post("/goals/{goal_id}/contribute")
def contribute_to_goal(
    goal_id: int,
    data: GoalContribution,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = goal_budget_service.contribute_to_goal(
        db=db,
        user_id=current_user.id,
        goal_id=goal_id,
        amount=data.amount
    )

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Financial goal not found."
        )

    return goal


# ============================================================
# BUDGETS
# ============================================================

@router.post(
    "/budgets",
    status_code=status.HTTP_201_CREATED
)
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return goal_budget_service.create_budget(
        db=db,
        user_id=current_user.id,
        name=data.name,
        amount=data.amount,
        category_id=data.category_id,
        period=data.period
    )


@router.get("/budgets")
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "budgets": goal_budget_service.get_budgets(
            db,
            current_user.id
        )
    }


# ============================================================
# COMPLETE PLANNING SUMMARY
# ============================================================

@router.get("/summary")
def planning_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "planning": goal_budget_service.summary(
            db,
            current_user.id
        )
    }
