from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.credit_card import CreditCard
from app.models.debt import Debt
from app.models.bill import Bill
from app.models.security_event import SecurityEvent
from app.models.user import User


class FinancialRiskIntelligenceService:

    def analyze_user(
        self,
        db: Session,
        user: User
    ):

        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).all()

        cards = db.query(CreditCard).filter(
            CreditCard.user_id == user.id
        ).all()

        debts = db.query(Debt).filter(
            Debt.user_id == user.id
        ).all()

        bills = db.query(Bill).filter(
            Bill.user_id == user.id
        ).all()

        security_events = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user.id
        ).all()

        # ----------------------------------------------------
        # TRANSACTION RISK
        # ----------------------------------------------------

        expense_transactions = [
            t for t in transactions
            if str(t.transaction_type).upper()
            in [
                "EXPENSE",
                "PAYMENT",
                "WITHDRAWAL",
                "DEBIT",
                "TRANSFER"
            ]
        ]

        transaction_risk = 0.0

        high_risk_transactions = 0
        critical_transactions = 0

        for transaction in expense_transactions:

            risk = float(
                transaction.fraud_risk_score or 0
            )

            transaction_risk = max(
                transaction_risk,
                risk
            )

            if risk >= 80:
                critical_transactions += 1

            elif risk >= 60:
                high_risk_transactions += 1

        # ----------------------------------------------------
        # CREDIT CARD RISK
        # ----------------------------------------------------

        total_limit = sum(
            float(card.credit_limit or 0)
            for card in cards
        )

        total_balance = sum(
            float(card.outstanding_balance or 0)
            for card in cards
        )

        credit_utilization = (
            (total_balance / total_limit) * 100
            if total_limit > 0
            else 0
        )

        if credit_utilization >= 90:
            credit_risk = 100

        elif credit_utilization >= 80:
            credit_risk = 85

        elif credit_utilization >= 70:
            credit_risk = 70

        elif credit_utilization >= 50:
            credit_risk = 45

        elif credit_utilization >= 30:
            credit_risk = 25

        else:
            credit_risk = 10

        # ----------------------------------------------------
        # DEBT RISK
        # ----------------------------------------------------

        total_debt = sum(
            float(debt.outstanding_amount or 0)
            for debt in debts
        )

        high_interest_debts = sum(
            1
            for debt in debts
            if float(debt.interest_rate or 0) >= 15
        )

        debt_risk = 0.0

        if total_debt > 100000:
            debt_risk += 35

        elif total_debt > 50000:
            debt_risk += 20

        elif total_debt > 0:
            debt_risk += 10

        debt_risk += high_interest_debts * 15

        debt_risk = min(
            debt_risk,
            100
        )

        # ----------------------------------------------------
        # BILL RISK
        # ----------------------------------------------------

        overdue_bills = 0
        upcoming_bills = 0

        now = datetime.utcnow()
        soon = now + timedelta(days=7)

        for bill in bills:

            if str(bill.status).upper() == "OVERDUE":
                overdue_bills += 1

            elif (
                bill.due_date
                and now <= bill.due_date <= soon
                and str(bill.status).upper() != "PAID"
            ):
                upcoming_bills += 1

        bill_risk = min(
            overdue_bills * 25
            + upcoming_bills * 5,
            100
        )

        # ----------------------------------------------------
        # SECURITY RISK
        # ----------------------------------------------------

        open_security_events = [
            event
            for event in security_events
            if str(event.status).lower() == "open"
        ]

        critical_security_events = sum(
            1
            for event in open_security_events
            if str(event.severity).upper() == "CRITICAL"
        )

        high_security_events = sum(
            1
            for event in open_security_events
            if str(event.severity).upper()
            in ["HIGH", "HIGH_RISK"]
        )

        security_risk = min(
            critical_security_events * 30
            + high_security_events * 15,
            100
        )

        # ----------------------------------------------------
        # COMBINED RISK
        # ----------------------------------------------------

        combined_risk = (
            transaction_risk * 0.35
            + credit_risk * 0.20
            + debt_risk * 0.15
            + bill_risk * 0.10
            + security_risk * 0.20
        )

        combined_risk = round(
            min(max(combined_risk, 0), 100),
            2
        )

        if combined_risk >= 80:
            risk_level = "CRITICAL"

        elif combined_risk >= 60:
            risk_level = "HIGH"

        elif combined_risk >= 35:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"

        # ----------------------------------------------------
        # RISK FACTORS
        # ----------------------------------------------------

        risk_factors = []

        if transaction_risk >= 60:
            risk_factors.append(
                "High-risk transactions detected."
            )

        if credit_utilization >= 70:
            risk_factors.append(
                "Credit card utilization is high."
            )

        if total_debt > 50000:
            risk_factors.append(
                "Outstanding debt exposure is significant."
            )

        if high_interest_debts > 0:
            risk_factors.append(
                "High-interest debt detected."
            )

        if overdue_bills > 0:
            risk_factors.append(
                "Overdue bills require attention."
            )

        if critical_security_events > 0:
            risk_factors.append(
                "Critical security events are still open."
            )

        if not risk_factors:
            risk_factors.append(
                "No major financial risk factors detected."
            )

        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        recommendations = []

        if transaction_risk >= 60:
            recommendations.append(
                "Review suspicious transactions immediately."
            )

        if credit_utilization >= 70:
            recommendations.append(
                "Reduce credit card balances to lower utilization."
            )

        if total_debt > 50000:
            recommendations.append(
                "Prioritize repayment of outstanding debt."
            )

        if high_interest_debts > 0:
            recommendations.append(
                "Prioritize high-interest debt repayment."
            )

        if overdue_bills > 0:
            recommendations.append(
                "Clear overdue bills as soon as possible."
            )

        if critical_security_events > 0:
            recommendations.append(
                "Review and resolve critical security alerts."
            )

        if not recommendations:
            recommendations.append(
                "Continue monitoring spending, debt and credit utilization."
            )

        return {
            "risk_score": combined_risk,
            "risk_level": risk_level,

            "components": {
                "transaction_risk": round(
                    transaction_risk,
                    2
                ),
                "credit_risk": round(
                    credit_risk,
                    2
                ),
                "debt_risk": round(
                    debt_risk,
                    2
                ),
                "bill_risk": round(
                    bill_risk,
                    2
                ),
                "security_risk": round(
                    security_risk,
                    2
                )
            },

            "metrics": {
                "credit_utilization": round(
                    credit_utilization,
                    2
                ),
                "total_debt": round(
                    total_debt,
                    2
                ),
                "overdue_bills": overdue_bills,
                "upcoming_bills": upcoming_bills,
                "high_risk_transactions":
                    high_risk_transactions,
                "critical_transactions":
                    critical_transactions,
                "open_security_events":
                    len(open_security_events)
            },

            "risk_factors": risk_factors,
            "recommendations": recommendations
        }


financial_risk_service = (
    FinancialRiskIntelligenceService()
)
