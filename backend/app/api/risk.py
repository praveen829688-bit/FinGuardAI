from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.services.financial_risk_intelligence_service import (
    financial_risk_service
)
from app.models.user import User


router = APIRouter(
    prefix="/api/risk",
    tags=["Financial Risk Intelligence"]
)


@router.get("/analysis")
def risk_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "analysis": result
    }


@router.get("/score")
def risk_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"]
    }


@router.get("/components")
def risk_components(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "components": result["components"]
    }


@router.get("/factors")
def risk_factors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "risk_level": result["risk_level"],
        "risk_factors": result["risk_factors"]
    }


@router.get("/recommendations")
def risk_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "risk_level": result["risk_level"],
        "recommendations": result["recommendations"]
    }


@router.get("/summary")
def risk_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    result = financial_risk_service.analyze_user(
        db=db,
        user=current_user
    )

    return {
        "user_id": current_user.id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "components": result["components"],
        "metrics": result["metrics"]
    }
