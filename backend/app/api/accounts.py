from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.account import Account
from app.models.user import User


router = APIRouter(
    prefix="/api/accounts",
    tags=["Financial Accounts"]
)


class AccountCreate(BaseModel):
    account_name: str = Field(min_length=2, max_length=100)
    account_type: str = Field(min_length=2, max_length=50)
    institution_name: str | None = None
    account_number_last4: str | None = Field(
        default=None,
        min_length=4,
        max_length=4
    )
    currency: str = "INR"
    balance: float = Field(default=0.0, ge=0)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = Account(
        user_id=current_user.id,
        account_name=data.account_name,
        account_type=data.account_type,
        institution_name=data.institution_name,
        account_number_last4=data.account_number_last4,
        currency=data.currency,
        balance=data.balance
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get("/")
def get_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Account).filter(
        Account.user_id == current_user.id
    ).all()


@router.get("/{account_id}")
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found."
        )

    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found."
        )

    account.is_active = 0
    db.commit()

    return {
        "message": "Account deactivated successfully."
    }
