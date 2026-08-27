from datetime import datetime

from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.financial_goal import FinancialGoal
from app.models.transaction import Transaction


class GoalBudgetService:

    # ========================================================
    # FINANCIAL GOALS
    # ========================================================

    def create_goal(
        self,
        db: Session,
        user_id: int,
        name: str,
        description: str | None,
        target_amount: float,
        target_date: datetime | None
    ):
        goal = FinancialGoal(
            user_id=user_id,
            name=name,
            description=description,
            target_amount=target_amount,
            current_amount=0.0,
            target_date=target_date,
            status="ACTIVE"
        )

        db.add(goal)
        db.commit()
        db.refresh(goal)

        return goal

    def get_goals(
        self,
        db: Session,
        user_id: int
    ):
        goals = db.query(
            FinancialGoal
        ).filter(
            FinancialGoal.user_id == user_id
        ).order_by(
            FinancialGoal.created_at.desc()
        ).all()

        result = []

        for goal in goals:

            target = float(
                goal.target_amount or 0
            )

            current = float(
                goal.current_amount or 0
            )

            percentage = (
                (current / target) * 100
                if target > 0
                else 0
            )

            percentage = min(
                round(percentage, 2),
                100
            )

            remaining = max(
                target - current,
                0
            )

            result.append({
                "id": goal.id,
                "name": goal.name,
                "description": goal.description,
                "target_amount": target,
                "current_amount": current,
                "remaining_amount": round(
                    remaining,
                    2
                ),
                "progress_percentage": percentage,
                "target_date": (
                    goal.target_date.isoformat()
                    if goal.target_date
                    else None
                ),
                "status": goal.status,
                "created_at": (
                    goal.created_at.isoformat()
                    if goal.created_at
                    else None
                )
            })

        return result

    def contribute_to_goal(
        self,
        db: Session,
        user_id: int,
        goal_id: int,
        amount: float
    ):
        goal = db.query(
            FinancialGoal
        ).filter(
            FinancialGoal.id == goal_id,
            FinancialGoal.user_id == user_id
        ).first()

        if not goal:
            return None

        goal.current_amount = (
            float(goal.current_amount or 0)
            + amount
        )

        if goal.current_amount >= goal.target_amount:
            goal.current_amount = (
                goal.target_amount
            )
            goal.status = "COMPLETED"

        db.commit()
        db.refresh(goal)

        return goal

    # ========================================================
    # BUDGETS
    # ========================================================

    def create_budget(
        self,
        db: Session,
        user_id: int,
        name: str,
        amount: float,
        category_id: int | None,
        period: str
    ):
        budget = Budget(
            user_id=user_id,
            name=name,
            amount=amount,
            category_id=category_id,
            period=period.upper(),
            status="ACTIVE"
        )

        db.add(budget)
        db.commit()
        db.refresh(budget)

        return budget

    def get_budgets(
        self,
        db: Session,
        user_id: int
    ):
        budgets = db.query(
            Budget
        ).filter(
            Budget.user_id == user_id
        ).order_by(
            Budget.created_at.desc()
        ).all()

        result = []

        for budget in budgets:

            spent = 0.0

            query = db.query(
                Transaction
            ).filter(
                Transaction.user_id == user_id
            )

            if budget.category_id is not None:

                query = query.filter(
                    Transaction.category_id
                    == budget.category_id
                )

            transactions = query.all()

            for transaction in transactions:

                transaction_type = (
                    transaction.transaction_type.upper()
                )

                if transaction_type in [
                    "EXPENSE",
                    "PAYMENT",
                    "WITHDRAWAL",
                    "DEBIT"
                ]:

                    spent += float(
                        transaction.amount or 0
                    )

            budget_amount = float(
                budget.amount or 0
            )

            remaining = max(
                budget_amount - spent,
                0
            )

            utilization = (
                (spent / budget_amount) * 100
                if budget_amount > 0
                else 0
            )

            utilization = round(
                utilization,
                2
            )

            if utilization >= 100:
                budget_status = "OVER_BUDGET"

            elif utilization >= 80:
                budget_status = "HIGH_USAGE"

            else:
                budget_status = "WITHIN_BUDGET"

            result.append({
                "id": budget.id,
                "name": budget.name,
                "category_id": budget.category_id,
                "budget_amount": budget_amount,
                "spent_amount": round(
                    spent,
                    2
                ),
                "remaining_amount": round(
                    remaining,
                    2
                ),
                "utilization_percentage": utilization,
                "budget_status": budget_status,
                "period": budget.period,
                "status": budget.status,
                "created_at": (
                    budget.created_at.isoformat()
                    if budget.created_at
                    else None
                )
            })

        return result

    # ========================================================
    # COMPLETE SUMMARY
    # ========================================================

    def summary(
        self,
        db: Session,
        user_id: int
    ):
        goals = self.get_goals(
            db,
            user_id
        )

        budgets = self.get_budgets(
            db,
            user_id
        )

        active_goals = [
            goal
            for goal in goals
            if goal["status"] == "ACTIVE"
        ]

        completed_goals = [
            goal
            for goal in goals
            if goal["status"] == "COMPLETED"
        ]

        over_budget = [
            budget
            for budget in budgets
            if budget["budget_status"]
            == "OVER_BUDGET"
        ]

        high_usage = [
            budget
            for budget in budgets
            if budget["budget_status"]
            == "HIGH_USAGE"
        ]

        return {
            "goals": {
                "total": len(goals),
                "active": len(active_goals),
                "completed": len(completed_goals),
                "items": goals
            },
            "budgets": {
                "total": len(budgets),
                "over_budget": len(over_budget),
                "high_usage": len(high_usage),
                "items": budgets
            }
        }


goal_budget_service = GoalBudgetService()
