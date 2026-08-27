from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.financial_intelligence_service import (
    financial_intelligence_service
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Financial Intelligence"]
)


@router.get("/monthly")
def monthly_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "months": (
            financial_intelligence_service
            .monthly_analytics(
                db,
                current_user.id
            )
        )
    }


@router.get("/categories")
def category_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "categories": (
            financial_intelligence_service
            .category_analysis(
                db,
                current_user.id
            )
        )
    }


@router.get("/insights")
def financial_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "insights": (
            financial_intelligence_service
            .spending_insights(
                db,
                current_user.id
            )
        )
    }


@router.get("/health")
def financial_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "financial_health": (
            financial_intelligence_service
            .financial_health(
                db,
                current_user.id
            )
        )
    }


@router.get("/summary")
def intelligence_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = financial_intelligence_service

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email
        },
        "monthly": service.monthly_analytics(
            db,
            current_user.id
        ),
        "categories": service.category_analysis(
            db,
            current_user.id
        ),
        "insights": service.spending_insights(
            db,
            current_user.id
        ),
        "financial_health": service.financial_health(
            db,
            current_user.id
        )
    }
