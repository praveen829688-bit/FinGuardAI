from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.financial_advisor_service import (
    financial_advisor_service
)


router = APIRouter(
    prefix="/api/advisor",
    tags=["AI Financial Advisor"]
)


@router.get("/insights")
def advisor_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        financial_advisor_service
        .generate_insights(
            db,
            current_user.id
        )
    )

    return {
        "user_id": current_user.id,
        "advisor": "FinGuard AI Financial Advisor",
        "insights": result["insights"],
        "financial_health": result[
            "financial_health"
        ]
    }


@router.get("/recommendations")
def advisor_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        financial_advisor_service
        .generate_recommendations(
            db,
            current_user.id
        )
    )

    return {
        "user_id": current_user.id,
        "advisor": "FinGuard AI Financial Advisor",
        "recommendations": result[
            "recommendations"
        ]
    }


@router.get("/summary")
def advisor_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        financial_advisor_service
        .summary(
            db,
            current_user.id
        )
    )

    return {
        "user_id": current_user.id,
        **result
    }
