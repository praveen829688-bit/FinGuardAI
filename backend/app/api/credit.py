from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.credit_card import CreditCard
from app.models.debt import Debt
from app.models.user import User


router = APIRouter(
    prefix="/api/credit",
    tags=["Credit Cards & Debt"]
)


# ============================================================
# SCHEMAS
# ============================================================

class CreditCardCreate(BaseModel):
    card_name: str = Field(min_length=2, max_length=150)
    issuer: str | None = None
    last4: str | None = Field(default=None, min_length=4, max_length=4)

    credit_limit: float = Field(gt=0)
    outstanding_balance: float = Field(default=0, ge=0)

    due_date: datetime | None = None
    minimum_due: float = Field(default=0, ge=0)
    interest_rate: float = Field(default=0, ge=0)


class CreditCardUpdate(BaseModel):
    card_name: str | None = None
    issuer: str | None = None
    credit_limit: float | None = Field(default=None, gt=0)
    outstanding_balance: float | None = Field(default=None, ge=0)
    due_date: datetime | None = None
    minimum_due: float | None = Field(default=None, ge=0)
    interest_rate: float | None = Field(default=None, ge=0)
    status: str | None = None


class CreditPayment(BaseModel):
    amount: float = Field(gt=0)


class DebtCreate(BaseModel):
    debt_name: str = Field(min_length=2, max_length=150)
    debt_type: str = Field(min_length=2, max_length=50)
    lender: str | None = None

    principal_amount: float = Field(gt=0)
    outstanding_amount: float = Field(gt=0)

    interest_rate: float = Field(default=0, ge=0)
    minimum_payment: float = Field(default=0, ge=0)

    due_date: datetime | None = None


class DebtUpdate(BaseModel):
    debt_name: str | None = None
    debt_type: str | None = None
    lender: str | None = None
    principal_amount: float | None = Field(default=None, gt=0)
    outstanding_amount: float | None = Field(default=None, ge=0)
    interest_rate: float | None = Field(default=None, ge=0)
    minimum_payment: float | None = Field(default=None, ge=0)
    due_date: datetime | None = None
    status: str | None = None


class DebtPayment(BaseModel):
    amount: float = Field(gt=0)


# ============================================================
# HELPERS
# ============================================================

def update_card_metrics(card: CreditCard):

    limit = float(card.credit_limit or 0)
    balance = float(card.outstanding_balance or 0)

    card.available_credit = max(
        limit - balance,
        0
    )

    card.utilization_percentage = (
        (balance / limit) * 100
        if limit > 0
        else 0
    )

    if card.utilization_percentage >= 90:
        card.status = "HIGH_RISK"

    elif card.utilization_percentage >= 70:
        card.status = "WARNING"

    elif card.status not in ["BLOCKED", "CLOSED"]:
        card.status = "ACTIVE"


def serialize_card(card: CreditCard):

    return {
        "id": card.id,
        "user_id": card.user_id,
        "card_name": card.card_name,
        "issuer": card.issuer,
        "last4": card.last4,
        "credit_limit": round(float(card.credit_limit or 0), 2),
        "outstanding_balance": round(
            float(card.outstanding_balance or 0),
            2
        ),
        "available_credit": round(
            float(card.available_credit or 0),
            2
        ),
        "utilization_percentage": round(
            float(card.utilization_percentage or 0),
            2
        ),
        "due_date": (
            card.due_date.isoformat()
            if card.due_date
            else None
        ),
        "minimum_due": round(
            float(card.minimum_due or 0),
            2
        ),
        "interest_rate": round(
            float(card.interest_rate or 0),
            2
        ),
        "status": card.status,
        "created_at": (
            card.created_at.isoformat()
            if card.created_at
            else None
        ),
        "updated_at": (
            card.updated_at.isoformat()
            if card.updated_at
            else None
        )
    }


def serialize_debt(debt: Debt):

    return {
        "id": debt.id,
        "user_id": debt.user_id,
        "debt_name": debt.debt_name,
        "debt_type": debt.debt_type,
        "lender": debt.lender,
        "principal_amount": round(
            float(debt.principal_amount or 0),
            2
        ),
        "outstanding_amount": round(
            float(debt.outstanding_amount or 0),
            2
        ),
        "interest_rate": round(
            float(debt.interest_rate or 0),
            2
        ),
        "minimum_payment": round(
            float(debt.minimum_payment or 0),
            2
        ),
        "due_date": (
            debt.due_date.isoformat()
            if debt.due_date
            else None
        ),
        "status": debt.status,
        "created_at": (
            debt.created_at.isoformat()
            if debt.created_at
            else None
        ),
        "updated_at": (
            debt.updated_at.isoformat()
            if debt.updated_at
            else None
        )
    }


# ============================================================
# CREDIT CARD ENDPOINTS
# ============================================================

@router.post("/cards")
def create_credit_card(
    data: CreditCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    card = CreditCard(
        user_id=current_user.id,
        card_name=data.card_name,
        issuer=data.issuer,
        last4=data.last4,
        credit_limit=data.credit_limit,
        outstanding_balance=data.outstanding_balance,
        due_date=data.due_date,
        minimum_due=data.minimum_due,
        interest_rate=data.interest_rate,
        status="ACTIVE"
    )

    update_card_metrics(card)

    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "message": "Credit card created successfully.",
        "card": serialize_card(card)
    }


@router.get("/cards")
def get_credit_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cards = db.query(CreditCard).filter(
        CreditCard.user_id == current_user.id
    ).order_by(
        CreditCard.id.desc()
    ).all()

    for card in cards:
        update_card_metrics(card)

    db.commit()

    return {
        "cards": [
            serialize_card(card)
            for card in cards
        ],
        "count": len(cards)
    }


@router.get("/cards/summary")
def credit_card_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cards = db.query(CreditCard).filter(
        CreditCard.user_id == current_user.id
    ).all()

    total_limit = 0.0
    total_outstanding = 0.0
    total_available = 0.0

    high_risk_cards = 0
    warning_cards = 0

    for card in cards:

        update_card_metrics(card)

        total_limit += float(
            card.credit_limit or 0
        )

        total_outstanding += float(
            card.outstanding_balance or 0
        )

        total_available += float(
            card.available_credit or 0
        )

        if card.status == "HIGH_RISK":
            high_risk_cards += 1

        elif card.status == "WARNING":
            warning_cards += 1

    db.commit()

    utilization = (
        (total_outstanding / total_limit) * 100
        if total_limit > 0
        else 0
    )

    return {
        "summary": {
            "total_cards": len(cards),
            "total_credit_limit": round(total_limit, 2),
            "total_outstanding": round(
                total_outstanding,
                2
            ),
            "total_available_credit": round(
                total_available,
                2
            ),
            "utilization_percentage": round(
                utilization,
                2
            ),
            "high_risk_cards": high_risk_cards,
            "warning_cards": warning_cards
        }
    }


@router.get("/cards/{card_id}")
def get_credit_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Credit card not found."
        )

    update_card_metrics(card)
    db.commit()

    return {
        "card": serialize_card(card)
    }


@router.put("/cards/{card_id}")
def update_credit_card(
    card_id: int,
    data: CreditCardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Credit card not found."
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(card, key, value)

    update_card_metrics(card)

    db.commit()
    db.refresh(card)

    return {
        "message": "Credit card updated successfully.",
        "card": serialize_card(card)
    }


@router.post("/cards/{card_id}/pay")
def pay_credit_card(
    card_id: int,
    data: CreditPayment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Credit card not found."
        )

    balance = float(
        card.outstanding_balance or 0
    )

    if data.amount > balance:
        raise HTTPException(
            status_code=400,
            detail="Payment cannot exceed outstanding balance."
        )

    card.outstanding_balance = (
        balance - data.amount
    )

    if card.minimum_due > 0:
        card.minimum_due = max(
            float(card.minimum_due) - data.amount,
            0
        )

    update_card_metrics(card)

    db.commit()
    db.refresh(card)

    return {
        "message": "Credit card payment recorded successfully.",
        "payment_amount": data.amount,
        "card": serialize_card(card)
    }


# ============================================================
# DEBT ENDPOINTS
# ============================================================

@router.post("/debts")
def create_debt(
    data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if data.outstanding_amount > data.principal_amount:
        raise HTTPException(
            status_code=400,
            detail="Outstanding amount cannot exceed principal amount."
        )

    debt = Debt(
        user_id=current_user.id,
        debt_name=data.debt_name,
        debt_type=data.debt_type.upper(),
        lender=data.lender,
        principal_amount=data.principal_amount,
        outstanding_amount=data.outstanding_amount,
        interest_rate=data.interest_rate,
        minimum_payment=data.minimum_payment,
        due_date=data.due_date,
        status="ACTIVE"
    )

    db.add(debt)
    db.commit()
    db.refresh(debt)

    return {
        "message": "Debt created successfully.",
        "debt": serialize_debt(debt)
    }


@router.get("/debts")
def get_debts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id
    ).order_by(
        Debt.id.desc()
    ).all()

    return {
        "debts": [
            serialize_debt(debt)
            for debt in debts
        ],
        "count": len(debts)
    }


@router.get("/debts/summary")
def debt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id
    ).all()

    total_principal = 0.0
    total_outstanding = 0.0
    total_minimum_payment = 0.0

    high_interest_debts = 0

    for debt in debts:

        total_principal += float(
            debt.principal_amount or 0
        )

        total_outstanding += float(
            debt.outstanding_amount or 0
        )

        total_minimum_payment += float(
            debt.minimum_payment or 0
        )

        if float(debt.interest_rate or 0) >= 15:
            high_interest_debts += 1

    return {
        "summary": {
            "total_debts": len(debts),
            "total_principal": round(
                total_principal,
                2
            ),
            "total_outstanding": round(
                total_outstanding,
                2
            ),
            "total_minimum_payment": round(
                total_minimum_payment,
                2
            ),
            "high_interest_debts": high_interest_debts
        }
    }


@router.get("/debts/{debt_id}")
def get_debt(
    debt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()

    if not debt:
        raise HTTPException(
            status_code=404,
            detail="Debt not found."
        )

    return {
        "debt": serialize_debt(debt)
    }


@router.put("/debts/{debt_id}")
def update_debt(
    debt_id: int,
    data: DebtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()

    if not debt:
        raise HTTPException(
            status_code=404,
            detail="Debt not found."
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():

        if key == "debt_type" and value:
            value = value.upper()

        setattr(
            debt,
            key,
            value
        )

    db.commit()
    db.refresh(debt)

    return {
        "message": "Debt updated successfully.",
        "debt": serialize_debt(debt)
    }


@router.post("/debts/{debt_id}/pay")
def pay_debt(
    debt_id: int,
    data: DebtPayment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()

    if not debt:
        raise HTTPException(
            status_code=404,
            detail="Debt not found."
        )

    outstanding = float(
        debt.outstanding_amount or 0
    )

    if data.amount > outstanding:
        raise HTTPException(
            status_code=400,
            detail="Payment cannot exceed outstanding debt."
        )

    debt.outstanding_amount = (
        outstanding - data.amount
    )

    if debt.outstanding_amount <= 0:
        debt.outstanding_amount = 0
        debt.status = "PAID"

    db.commit()
    db.refresh(debt)

    return {
        "message": "Debt payment recorded successfully.",
        "payment_amount": data.amount,
        "debt": serialize_debt(debt)
    }


# ============================================================
# OVERALL CREDIT & DEBT SUMMARY
# ============================================================

@router.get("/summary")
def credit_debt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cards = db.query(CreditCard).filter(
        CreditCard.user_id == current_user.id
    ).all()

    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id
    ).all()

    total_credit_limit = 0.0
    total_card_balance = 0.0

    for card in cards:

        update_card_metrics(card)

        total_credit_limit += float(
            card.credit_limit or 0
        )

        total_card_balance += float(
            card.outstanding_balance or 0
        )

    total_debt = sum(
        float(debt.outstanding_amount or 0)
        for debt in debts
    )

    total_minimum_payment = (
        sum(
            float(card.minimum_due or 0)
            for card in cards
        )
        +
        sum(
            float(debt.minimum_payment or 0)
            for debt in debts
        )
    )

    combined_liability = (
        total_card_balance + total_debt
    )

    utilization = (
        (total_card_balance / total_credit_limit) * 100
        if total_credit_limit > 0
        else 0
    )

    if utilization >= 80:
        risk_status = "HIGH"

    elif utilization >= 50:
        risk_status = "MEDIUM"

    else:
        risk_status = "LOW"

    db.commit()

    return {
        "summary": {
            "credit_cards": len(cards),
            "debts": len(debts),
            "total_credit_limit": round(
                total_credit_limit,
                2
            ),
            "credit_card_outstanding": round(
                total_card_balance,
                2
            ),
            "total_debt_outstanding": round(
                total_debt,
                2
            ),
            "combined_liability": round(
                combined_liability,
                2
            ),
            "total_minimum_payment": round(
                total_minimum_payment,
                2
            ),
            "credit_utilization_percentage": round(
                utilization,
                2
            ),
            "debt_risk": risk_status
        }
    }
