from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.investment import Investment
from app.models.user import User


router = APIRouter(
    prefix="/api/investments",
    tags=["Investment & Wealth Management"]
)


class InvestmentCreate(BaseModel):

    investment_type: str = Field(
        min_length=2,
        max_length=50
    )

    name: str = Field(
        min_length=2,
        max_length=150
    )

    platform: str | None = None

    invested_amount: float = Field(
        gt=0
    )

    current_value: float = Field(
        gt=0
    )

    units: float | None = Field(
        default=None,
        gt=0
    )

    purchase_price: float | None = Field(
        default=None,
        gt=0
    )

    current_price: float | None = Field(
        default=None,
        gt=0
    )

    purchase_date: datetime | None = None


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_investment(
    data: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    investment = Investment(
        user_id=current_user.id,
        investment_type=data.investment_type.upper(),
        name=data.name,
        platform=data.platform,
        invested_amount=data.invested_amount,
        current_value=data.current_value,
        units=data.units,
        purchase_price=data.purchase_price,
        current_price=data.current_price,
        purchase_date=data.purchase_date,
        status="ACTIVE"
    )

    db.add(investment)
    db.commit()
    db.refresh(investment)

    profit_loss = (
        investment.current_value
        - investment.invested_amount
    )

    return {
        "investment": investment,
        "profit_loss": round(
            profit_loss,
            2
        ),
        "return_percentage": round(
            (
                profit_loss
                / investment.invested_amount
            ) * 100,
            2
        )
    }


@router.get("/")
def get_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    investments = db.query(
        Investment
    ).filter(
        Investment.user_id == current_user.id
    ).order_by(
        Investment.created_at.desc()
    ).all()

    return {
        "investments": investments,
        "count": len(investments)
    }


@router.get("/summary")
def investment_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    investments = db.query(
        Investment
    ).filter(
        Investment.user_id == current_user.id,
        Investment.status == "ACTIVE"
    ).all()

    total_invested = sum(
        float(item.invested_amount or 0)
        for item in investments
    )

    total_current_value = sum(
        float(item.current_value or 0)
        for item in investments
    )

    total_profit_loss = (
        total_current_value
        - total_invested
    )

    return_percentage = (
        (
            total_profit_loss
            / total_invested
        ) * 100
        if total_invested > 0
        else 0
    )

    allocation = {}

    for item in investments:

        investment_type = (
            item.investment_type
            or "OTHER"
        ).upper()

        allocation[investment_type] = (
            allocation.get(
                investment_type,
                0
            )
            + float(
                item.current_value or 0
            )
        )

    allocation_result = [
        {
            "investment_type": key,
            "current_value": round(
                value,
                2
            ),
            "percentage": round(
                (
                    value
                    / total_current_value
                ) * 100,
                2
            )
            if total_current_value > 0
            else 0
        }
        for key, value
        in sorted(
            allocation.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]

    return {
        "portfolio": {
            "total_investments": len(
                investments
            ),
            "total_invested": round(
                total_invested,
                2
            ),
            "current_value": round(
                total_current_value,
                2
            ),
            "profit_loss": round(
                total_profit_loss,
                2
            ),
            "return_percentage": round(
                return_percentage,
                2
            )
        },
        "allocation": allocation_result
    }


@router.get("/{investment_id}")
def get_investment(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    investment = db.query(
        Investment
    ).filter(
        Investment.id == investment_id,
        Investment.user_id == current_user.id
    ).first()

    if not investment:

        raise HTTPException(
            status_code=404,
            detail="Investment not found."
        )

    profit_loss = (
        float(
            investment.current_value or 0
        )
        - float(
            investment.invested_amount or 0
        )
    )

    return {
        "investment": investment,
        "profit_loss": round(
            profit_loss,
            2
        ),
        "return_percentage": round(
            (
                profit_loss
                / float(
                    investment.invested_amount
                )
            ) * 100,
            2
        )
        if investment.invested_amount
        else 0
    }
