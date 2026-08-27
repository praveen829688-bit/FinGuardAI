from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.transaction import Transaction
from app.models.user import User


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Financial Dashboard"]
)


@router.get("/monthly")
def monthly_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = db.query(
        Transaction
    ).filter(
        Transaction.user_id == current_user.id
    ).all()

    monthly = defaultdict(
        lambda: {
            "income": 0.0,
            "expenses": 0.0,
            "transactions": 0
        }
    )

    for transaction in transactions:

        if not transaction.created_at:
            continue

        month_key = transaction.created_at.strftime(
            "%Y-%m"
        )

        transaction_type = (
            transaction.transaction_type.upper()
        )

        amount = float(
            transaction.amount or 0
        )

        monthly[month_key]["transactions"] += 1

        if transaction_type in [
            "INCOME",
            "DEPOSIT",
            "CREDIT"
        ]:
            monthly[month_key]["income"] += amount

        elif transaction_type in [
            "EXPENSE",
            "PAYMENT",
            "WITHDRAWAL",
            "DEBIT"
        ]:
            monthly[month_key]["expenses"] += amount

    result = []

    for month in sorted(monthly.keys()):

        income = monthly[month]["income"]
        expenses = monthly[month]["expenses"]

        savings = income - expenses

        savings_rate = (
            (savings / income) * 100
            if income > 0
            else 0
        )

        result.append({
            "month": month,
            "income": round(
                income,
                2
            ),
            "expenses": round(
                expenses,
                2
            ),
            "savings": round(
                savings,
                2
            ),
            "savings_rate": round(
                savings_rate,
                2
            ),
            "transactions": (
                monthly[month]["transactions"]
            )
        })

    return {
        "months": result
    }
