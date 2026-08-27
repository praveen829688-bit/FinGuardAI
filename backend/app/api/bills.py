from datetime import datetime, timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.bill import Bill
from app.models.user import User


router = APIRouter(
    prefix="/api/bills",
    tags=["Bills & Recurring Payments"]
)


class BillCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150
    )

    bill_type: str = Field(
        min_length=2,
        max_length=50
    )

    provider: str | None = None

    amount: float = Field(
        gt=0
    )

    due_date: datetime

    frequency: str = Field(
        default="ONE_TIME",
        min_length=2,
        max_length=30
    )

    auto_pay: bool = False

    description: str | None = None


class BillUpdate(BaseModel):

    name: str | None = None
    bill_type: str | None = None
    provider: str | None = None
    amount: float | None = Field(
        default=None,
        gt=0
    )
    due_date: datetime | None = None
    frequency: str | None = None
    auto_pay: bool | None = None
    description: str | None = None


def serialize_bill(bill: Bill):

    return {
        "id": bill.id,
        "user_id": bill.user_id,
        "name": bill.name,
        "bill_type": bill.bill_type,
        "provider": bill.provider,
        "amount": float(bill.amount or 0),
        "due_date": (
            bill.due_date.isoformat()
            if bill.due_date
            else None
        ),
        "frequency": bill.frequency,
        "status": bill.status,
        "auto_pay": bool(bill.auto_pay),
        "description": bill.description,
        "last_paid_date": (
            bill.last_paid_date.isoformat()
            if bill.last_paid_date
            else None
        ),
        "next_due_date": (
            bill.next_due_date.isoformat()
            if bill.next_due_date
            else None
        ),
        "created_at": (
            bill.created_at.isoformat()
            if bill.created_at
            else None
        ),
        "updated_at": (
            bill.updated_at.isoformat()
            if bill.updated_at
            else None
        )
    }


def calculate_status(bill: Bill):

    if bill.status == "PAID":
        return "PAID"

    now = datetime.utcnow()

    if bill.due_date < now:
        return "OVERDUE"

    if bill.due_date <= now + timedelta(days=7):
        return "DUE_SOON"

    return "PENDING"


def advance_recurring_date(bill: Bill):

    if not bill.due_date:
        return

    frequency = (
        bill.frequency or "ONE_TIME"
    ).upper()

    if frequency == "WEEKLY":
        bill.due_date += timedelta(days=7)

    elif frequency == "BIWEEKLY":
        bill.due_date += timedelta(days=14)

    elif frequency == "MONTHLY":
        bill.due_date += timedelta(days=30)

    elif frequency == "QUARTERLY":
        bill.due_date += timedelta(days=90)

    elif frequency == "YEARLY":
        bill.due_date += timedelta(days=365)

    else:
        return

    bill.next_due_date = bill.due_date


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_bill(
    data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bill = Bill(
        user_id=current_user.id,
        name=data.name,
        bill_name=data.name,
        bill_type=data.bill_type,
        provider=data.provider,
        amount=data.amount,
        due_date=data.due_date,
        frequency=data.frequency.upper(),
        status="PENDING",
        auto_pay=1 if data.auto_pay else 0,
        description=data.description,
        next_due_date=data.due_date
    )

    bill.status = calculate_status(bill)

    db.add(bill)
    db.commit()
    db.refresh(bill)

    return {
        "message": "Bill created successfully.",
        "bill": serialize_bill(bill)
    }


@router.get("/")
def get_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).order_by(
        Bill.due_date.asc()
    ).all()

    for bill in bills:

        if bill.status != "PAID":
            bill.status = calculate_status(bill)

    db.commit()

    return {
        "bills": [
            serialize_bill(bill)
            for bill in bills
        ],
        "count": len(bills)
    }


@router.get("/upcoming")
def get_upcoming_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    now = datetime.utcnow()

    limit = (
        now + timedelta(days=30)
    )

    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        Bill.status != "PAID",
        Bill.due_date >= now,
        Bill.due_date <= limit
    ).order_by(
        Bill.due_date.asc()
    ).all()

    return {
        "bills": [
            serialize_bill(bill)
            for bill in bills
        ],
        "count": len(bills)
    }


@router.get("/overdue")
def get_overdue_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    now = datetime.utcnow()

    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        Bill.status != "PAID",
        Bill.due_date < now
    ).order_by(
        Bill.due_date.asc()
    ).all()

    for bill in bills:
        bill.status = "OVERDUE"

    db.commit()

    return {
        "bills": [
            serialize_bill(bill)
            for bill in bills
        ],
        "count": len(bills)
    }


@router.get("/summary")
def bills_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).all()

    total_amount = 0.0
    pending_amount = 0.0
    overdue_amount = 0.0
    paid_amount = 0.0

    overdue_count = 0
    due_soon_count = 0
    paid_count = 0

    for bill in bills:

        amount = float(
            bill.amount or 0
        )

        status_value = (
            calculate_status(bill)
            if bill.status != "PAID"
            else "PAID"
        )

        bill.status = status_value

        total_amount += amount

        if status_value == "PAID":
            paid_amount += amount
            paid_count += 1

        elif status_value == "OVERDUE":
            overdue_amount += amount
            overdue_count += 1

        elif status_value == "DUE_SOON":
            pending_amount += amount
            due_soon_count += 1

        else:
            pending_amount += amount

    db.commit()

    return {
        "summary": {
            "total_bills": len(bills),
            "total_amount": round(
                total_amount,
                2
            ),
            "pending_amount": round(
                pending_amount,
                2
            ),
            "overdue_amount": round(
                overdue_amount,
                2
            ),
            "paid_amount": round(
                paid_amount,
                2
            ),
            "overdue_count": overdue_count,
            "due_soon_count": due_soon_count,
            "paid_count": paid_count
        }
    }


@router.get("/{bill_id}")
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    if bill.status != "PAID":
        bill.status = calculate_status(bill)
        db.commit()

    return {
        "bill": serialize_bill(bill)
    }


@router.put("/{bill_id}")
def update_bill(
    bill_id: int,
    data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():

        if key == "auto_pay":
            value = 1 if value else 0

        if key == "frequency" and value:
            value = value.upper()

        setattr(
            bill,
            key,
            value
        )

    if bill.status != "PAID":
        bill.status = calculate_status(bill)

    db.commit()
    db.refresh(bill)

    return {
        "message": "Bill updated successfully.",
        "bill": serialize_bill(bill)
    }


@router.post("/{bill_id}/pay")
def pay_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    if bill.status == "PAID":
        raise HTTPException(
            status_code=400,
            detail="Bill is already paid."
        )

    now = datetime.utcnow()

    bill.last_paid_date = now

    frequency = (
        bill.frequency or "ONE_TIME"
    ).upper()

    if frequency == "ONE_TIME":

        bill.status = "PAID"
        bill.next_due_date = None

    else:

        advance_recurring_date(
            bill
        )

        bill.status = calculate_status(
            bill
        )

    db.commit()
    db.refresh(bill)

    return {
        "message": "Bill payment recorded successfully.",
        "payment_amount": float(
            bill.amount or 0
        ),
        "bill": serialize_bill(bill)
    }


@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found."
        )

    db.delete(bill)
    db.commit()

    return {
        "message": "Bill deleted successfully."
    }

