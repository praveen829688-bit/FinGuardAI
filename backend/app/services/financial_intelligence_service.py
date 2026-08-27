from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User


INCOME_TYPES = {
    "INCOME",
    "DEPOSIT",
    "CREDIT"
}

EXPENSE_TYPES = {
    "EXPENSE",
    "PAYMENT",
    "WITHDRAWAL",
    "DEBIT"
}


class FinancialIntelligenceService:

    def _transactions(
        self,
        db: Session,
        user_id: int
    ):
        return (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.asc())
            .all()
        )

    def monthly_analytics(
        self,
        db: Session,
        user_id: int
    ):
        transactions = self._transactions(
            db,
            user_id
        )

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

            month = transaction.created_at.strftime(
                "%Y-%m"
            )

            amount = float(
                transaction.amount or 0
            )

            transaction_type = (
                transaction.transaction_type.upper()
            )

            monthly[month]["transactions"] += 1

            if transaction_type in INCOME_TYPES:
                monthly[month]["income"] += amount

            elif transaction_type in EXPENSE_TYPES:
                monthly[month]["expenses"] += amount

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
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "savings": round(savings, 2),
                "savings_rate": round(
                    savings_rate,
                    2
                ),
                "transactions": monthly[month][
                    "transactions"
                ]
            })

        return result

    def category_analysis(
        self,
        db: Session,
        user_id: int
    ):
        transactions = self._transactions(
            db,
            user_id
        )

        categories = defaultdict(float)

        for transaction in transactions:

            transaction_type = (
                transaction.transaction_type.upper()
            )

            if transaction_type not in EXPENSE_TYPES:
                continue

            category = (
                str(transaction.category_id)
                if transaction.category_id
                else "Uncategorized"
            )

            categories[category] += float(
                transaction.amount or 0
            )

        total = sum(categories.values())

        result = []

        for category, amount in sorted(
            categories.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            percentage = (
                (amount / total) * 100
                if total > 0
                else 0
            )

            result.append({
                "category": category,
                "amount": round(amount, 2),
                "percentage": round(
                    percentage,
                    2
                )
            })

        return result

    def spending_insights(
        self,
        db: Session,
        user_id: int
    ):
        transactions = self._transactions(
            db,
            user_id
        )

        total_income = 0.0
        total_expenses = 0.0

        highest_expense = None
        expense_count = 0

        for transaction in transactions:

            amount = float(
                transaction.amount or 0
            )

            transaction_type = (
                transaction.transaction_type.upper()
            )

            if transaction_type in INCOME_TYPES:

                total_income += amount

            elif transaction_type in EXPENSE_TYPES:

                total_expenses += amount
                expense_count += 1

                if (
                    highest_expense is None
                    or amount > highest_expense["amount"]
                ):
                    highest_expense = {
                        "amount": amount,
                        "merchant": (
                            transaction.merchant_name
                            or "Unknown"
                        ),
                        "transaction_id": (
                            transaction.id
                        )
                    }

        savings = total_income - total_expenses

        savings_rate = (
            (savings / total_income) * 100
            if total_income > 0
            else 0
        )

        recommendations = []

        if total_income <= 0:

            recommendations.append(
                "Add income transactions to generate meaningful financial insights."
            )

        elif savings_rate < 10:

            recommendations.append(
                "Your savings rate is low. Consider reducing discretionary expenses."
            )

        elif savings_rate < 20:

            recommendations.append(
                "Your savings rate is moderate. Try increasing monthly savings."
            )

        else:

            recommendations.append(
                "Your savings rate is healthy. Continue maintaining disciplined spending."
            )

        if total_expenses > total_income:

            recommendations.append(
                "Expenses currently exceed income. Review recurring and discretionary spending."
            )

        if highest_expense:

            recommendations.append(
                f"Your largest recorded expense is "
                f"{highest_expense['amount']:.2f} "
                f"at {highest_expense['merchant']}."
            )

        return {
            "total_income": round(
                total_income,
                2
            ),
            "total_expenses": round(
                total_expenses,
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
            "expense_count": expense_count,
            "largest_expense": highest_expense,
            "recommendations": recommendations
        }

    def financial_health(
        self,
        db: Session,
        user_id: int
    ):
        accounts = (
            db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.is_active == 1
            )
            .all()
        )

        insights = self.spending_insights(
            db,
            user_id
        )

        savings_rate = insights["savings_rate"]

        if insights["total_income"] <= 0:

            score = 25

        elif savings_rate >= 30:

            score = 95

        elif savings_rate >= 20:

            score = 85

        elif savings_rate >= 10:

            score = 70

        elif savings_rate > 0:

            score = 55

        else:

            score = 35

        total_balance = sum(
            float(account.balance or 0)
            for account in accounts
        )

        if total_balance > 0:
            score = min(
                100,
                score + 5
            )

        if score >= 85:
            status = "EXCELLENT"

        elif score >= 70:
            status = "GOOD"

        elif score >= 50:
            status = "MODERATE"

        else:
            status = "NEEDS_ATTENTION"

        return {
            "score": score,
            "status": status,
            "total_balance": round(
                total_balance,
                2
            ),
            "savings_rate": savings_rate,
            "recommendations": insights[
                "recommendations"
            ]
        }


financial_intelligence_service = (
    FinancialIntelligenceService()
)
