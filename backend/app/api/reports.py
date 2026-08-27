import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db

from app.models.transaction import Transaction
from app.models.investment import Investment
from app.models.bill import Bill
from app.models.credit_card import CreditCard
from app.models.debt import Debt
from app.models.user import User

from app.services.financial_risk_intelligence_service import (
    financial_risk_service
)


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports & Export"]
)


def build_report(
    db: Session,
    current_user: User
):

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    investments = db.query(Investment).filter(
        Investment.user_id == current_user.id
    ).all()

    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).all()

    cards = db.query(CreditCard).filter(
        CreditCard.user_id == current_user.id
    ).all()

    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id
    ).all()

    risk = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    income = 0.0
    expenses = 0.0

    for transaction in transactions:

        transaction_type = str(
            transaction.transaction_type or ""
        ).upper()

        amount = float(
            transaction.amount or 0
        )

        if transaction_type in [
            "INCOME",
            "CREDIT",
            "DEPOSIT"
        ]:
            income += amount

        elif transaction_type in [
            "EXPENSE",
            "DEBIT",
            "PAYMENT",
            "WITHDRAWAL",
            "TRANSFER"
        ]:
            expenses += amount

    total_invested = sum(
        float(x.invested_amount or 0)
        for x in investments
    )

    current_investment_value = sum(
        float(x.current_value or 0)
        for x in investments
    )

    investment_profit = (
        current_investment_value
        - total_invested
    )

    total_credit_limit = sum(
        float(x.credit_limit or 0)
        for x in cards
    )

    total_credit_balance = sum(
        float(x.outstanding_balance or 0)
        for x in cards
    )

    credit_utilization = (
        (
            total_credit_balance
            / total_credit_limit
        ) * 100
        if total_credit_limit > 0
        else 0
    )

    total_debt = sum(
        float(x.outstanding_amount or 0)
        for x in debts
    )

    total_bills = sum(
        float(x.amount or 0)
        for x in bills
    )

    return {
        "report": {
            "generated_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id
        },

        "cash_flow": {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "net_cash_flow": round(
                income - expenses,
                2
            )
        },

        "investments": {
            "count": len(investments),
            "invested_amount": round(
                total_invested,
                2
            ),
            "current_value": round(
                current_investment_value,
                2
            ),
            "profit_loss": round(
                investment_profit,
                2
            )
        },

        "credit": {
            "total_limit": round(
                total_credit_limit,
                2
            ),
            "outstanding_balance": round(
                total_credit_balance,
                2
            ),
            "utilization_percentage": round(
                credit_utilization,
                2
            )
        },

        "debt": {
            "total_outstanding": round(
                total_debt,
                2
            ),
            "count": len(debts)
        },

        "bills": {
            "count": len(bills),
            "total_amount": round(
                total_bills,
                2
            )
        },

        "risk": risk
    }


@router.get("/summary")
def report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return build_report(
        db,
        current_user
    )


@router.get("/json")
def export_json(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    report = build_report(
        db,
        current_user
    )

    return report


@router.get("/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    report = build_report(
        db,
        current_user
    )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Section",
        "Metric",
        "Value"
    ])

    for section, values in report.items():

        if isinstance(values, dict):

            for key, value in values.items():

                if isinstance(value, (dict, list)):
                    value = json.dumps(
                        value,
                        default=str
                    )

                writer.writerow([
                    section,
                    key,
                    value
                ])

    output.seek(0)

    filename = (
        "finguard_financial_report.csv"
    )

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }
    )


@router.get("/risk")
def risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "risk_report": result
    }


@router.get("/wealth")
def wealth_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    investments = db.query(Investment).filter(
        Investment.user_id == current_user.id
    ).all()

    total_invested = sum(
        float(x.invested_amount or 0)
        for x in investments
    )

    current_value = sum(
        float(x.current_value or 0)
        for x in investments
    )

    return {
        "user_id": current_user.id,
        "wealth_report": {
            "investment_count": len(
                investments
            ),
            "total_invested": round(
                total_invested,
                2
            ),
            "current_value": round(
                current_value,
                2
            ),
            "profit_loss": round(
                current_value - total_invested,
                2
            )
        }
    }
