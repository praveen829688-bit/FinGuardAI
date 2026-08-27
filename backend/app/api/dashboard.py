from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.account import Account
from app.models.category import Category
from app.models.security_event import SecurityEvent
from app.models.transaction import Transaction
from app.models.user import User


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Financial Dashboard"]
)


@router.get("/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    accounts = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_active == 1
    ).all()

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(
        Transaction.created_at.desc()
    ).all()

    security_events = db.query(
        SecurityEvent
    ).filter(
        SecurityEvent.user_id == current_user.id
    ).order_by(
        SecurityEvent.created_at.desc()
    ).all()

    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).all()

    category_map = {
        category.id: category.name
        for category in categories
    }

    total_balance = sum(
        float(account.balance or 0)
        for account in accounts
    )

    income = 0.0
    expenses = 0.0

    income_transactions = []
    expense_transactions = []

    for transaction in transactions:

        transaction_type = (
            transaction.transaction_type.upper()
        )

        amount = float(
            transaction.amount or 0
        )

        if transaction_type in [
            "INCOME",
            "DEPOSIT",
            "CREDIT"
        ]:
            income += amount
            income_transactions.append(transaction)

        elif transaction_type in [
            "EXPENSE",
            "PAYMENT",
            "WITHDRAWAL",
            "DEBIT"
        ]:
            expenses += amount
            expense_transactions.append(transaction)

    savings = income - expenses

    savings_rate = (
        (savings / income) * 100
        if income > 0
        else 0
    )

    expense_ratio = (
        (expenses / income) * 100
        if income > 0
        else 0
    )

    income_expense_ratio = (
        income / expenses
        if expenses > 0
        else income
    )

    average_transaction = (
        sum(
            float(t.amount or 0)
            for t in transactions
        ) / len(transactions)
        if transactions
        else 0
    )

    largest_transaction = max(
        (
            float(t.amount or 0)
            for t in transactions
        ),
        default=0
    )

    largest_transaction_record = None

    if transactions:
        largest_transaction_record = max(
            transactions,
            key=lambda t: float(
                t.amount or 0
            )
        )

    fraud_events = [
        event
        for event in security_events
        if event.event_type == "TRANSACTION_RISK"
    ]

    phishing_events = [
        event
        for event in security_events
        if event.event_type == "PHISHING_URL"
    ]

    open_events = [
        event
        for event in security_events
        if event.status == "open"
    ]

    critical_alerts = sum(
        1
        for event in open_events
        if event.severity == "CRITICAL"
    )

    high_risk_alerts = sum(
        1
        for event in open_events
        if event.severity == "HIGH_RISK"
    )

    medium_risk_alerts = sum(
        1
        for event in open_events
        if event.severity in [
            "MEDIUM",
            "MEDIUM_RISK"
        ]
    )

    security_score = max(
        0,
        100
        - (critical_alerts * 20)
        - (high_risk_alerts * 10)
        - (medium_risk_alerts * 5)
    )

    if income <= 0:
        financial_health = 25
        financial_health_status = "NEEDS_ATTENTION"

    elif savings_rate >= 30:
        financial_health = 95
        financial_health_status = "EXCELLENT"

    elif savings_rate >= 20:
        financial_health = 85
        financial_health_status = "VERY_GOOD"

    elif savings_rate >= 10:
        financial_health = 70
        financial_health_status = "GOOD"

    elif savings_rate > 0:
        financial_health = 55
        financial_health_status = "MODERATE"

    else:
        financial_health = 35
        financial_health_status = "AT_RISK"

    if expense_ratio <= 50:
        spending_health = "HEALTHY"

    elif expense_ratio <= 75:
        spending_health = "MODERATE"

    elif expense_ratio <= 90:
        spending_health = "HIGH"

    else:
        spending_health = "CRITICAL"

    category_totals = defaultdict(float)

    for transaction in expense_transactions:

        category_id = transaction.category_id

        category_name = (
            category_map.get(
                category_id,
                "Uncategorized"
            )
            if category_id
            else "Uncategorized"
        )

        category_totals[
            category_name
        ] += float(
            transaction.amount or 0
        )

    total_category_expenses = sum(
        category_totals.values()
    )

    expense_categories = []

    for category, amount in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        percentage = (
            (amount / total_category_expenses) * 100
            if total_category_expenses > 0
            else 0
        )

        expense_categories.append({
            "category": category,
            "amount": round(
                amount,
                2
            ),
            "percentage": round(
                percentage,
                2
            )
        })

    top_spending_category = (
        expense_categories[0]
        if expense_categories
        else None
    )

    risk_scores = [
        float(
            transaction.fraud_risk_score or 0
        )
        for transaction in transactions
    ]

    average_risk_score = (
        sum(risk_scores) / len(risk_scores)
        if risk_scores
        else 0
    )

    high_risk_transactions = [
        transaction
        for transaction in transactions
        if float(
            transaction.fraud_risk_score or 0
        ) >= 70
    ]

    recent_transactions = []

    for transaction in transactions[:10]:

        category_name = (
            category_map.get(
                transaction.category_id,
                "Uncategorized"
            )
            if transaction.category_id
            else "Uncategorized"
        )

        recent_transactions.append({
            "id": transaction.id,
            "reference": (
                transaction.transaction_reference
            ),
            "type": transaction.transaction_type,
            "amount": round(
                float(transaction.amount or 0),
                2
            ),
            "category": category_name,
            "merchant": transaction.merchant_name,
            "status": transaction.status,
            "risk_score": round(
                float(
                    transaction.fraud_risk_score or 0
                ),
                2
            ),
            "fraud_status": transaction.fraud_status,
            "created_at": (
                transaction.created_at.isoformat()
                if transaction.created_at
                else None
            )
        })

    recent_security_events = []

    for event in security_events[:10]:

        recent_security_events.append({
            "id": event.id,
            "type": event.event_type,
            "severity": event.severity,
            "risk_score": round(
                float(event.risk_score or 0),
                2
            ),
            "title": event.title,
            "status": event.status,
            "created_at": (
                event.created_at.isoformat()
                if event.created_at
                else None
            )
        })

    if financial_health >= 85:
        financial_recommendation = (
            "Your savings performance is strong. "
            "Continue maintaining disciplined spending."
        )

    elif financial_health >= 70:
        financial_recommendation = (
            "Your finances are healthy. "
            "Consider increasing monthly savings."
        )

    elif financial_health >= 50:
        financial_recommendation = (
            "Your savings could improve. "
            "Review discretionary spending."
        )

    else:
        financial_recommendation = (
            "Your expenses require attention. "
            "Consider reducing non-essential spending."
        )

    if security_score >= 90:
        security_status = "SECURE"

    elif security_score >= 70:
        security_status = "MONITOR"

    elif security_score >= 50:
        security_status = "ELEVATED_RISK"

    else:
        security_status = "HIGH_RISK"

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email
        },

        "financial_summary": {
            "total_balance": round(
                total_balance,
                2
            ),
            "total_income": round(
                income,
                2
            ),
            "total_expenses": round(
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
            "expense_ratio": round(
                expense_ratio,
                2
            ),
            "income_expense_ratio": round(
                income_expense_ratio,
                2
            ),
            "financial_health_score": financial_health,
            "financial_health_status": (
                financial_health_status
            ),
            "financial_recommendation": (
                financial_recommendation
            )
        },

        "spending_intelligence": {
            "spending_health": spending_health,
            "average_transaction": round(
                average_transaction,
                2
            ),
            "largest_transaction": round(
                largest_transaction,
                2
            ),
            "largest_transaction_type": (
                largest_transaction_record.transaction_type
                if largest_transaction_record
                else None
            ),
            "top_spending_category": (
                top_spending_category
            ),
            "expense_categories": (
                expense_categories
            )
        },

        "security_summary": {
            "security_score": security_score,
            "security_status": security_status,
            "open_alerts": len(open_events),
            "fraud_alerts": len(fraud_events),
            "phishing_alerts": len(phishing_events),
            "critical_alerts": critical_alerts,
            "high_risk_alerts": high_risk_alerts,
            "medium_risk_alerts": medium_risk_alerts,
            "average_transaction_risk": round(
                average_risk_score,
                2
            ),
            "high_risk_transactions": len(
                high_risk_transactions
            )
        },

        "account_summary": {
            "total_accounts": len(accounts),
            "active_accounts": len(accounts),
            "accounts": [
                {
                    "id": account.id,
                    "name": account.account_name,
                    "type": account.account_type,
                    "balance": round(
                        float(account.balance or 0),
                        2
                    ),
                    "currency": account.currency
                }
                for account in accounts
            ]
        },

        "transaction_summary": {
            "total_transactions": len(
                transactions
            ),
            "income_transactions": len(
                income_transactions
            ),
            "expense_transactions": len(
                expense_transactions
            )
        },

        "recent_transactions": (
            recent_transactions
        ),

        "recent_security_events": (
            recent_security_events
        )
    }
