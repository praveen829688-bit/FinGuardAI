from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.notification_preference import (
    NotificationPreference
)
from app.models.user import User


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: bool = True
    mobile_enabled: bool = False
    critical_alerts: bool = True
    high_risk_alerts: bool = True


def get_or_create_preferences(
    db: Session,
    user_id: int
):
    preferences = db.query(
        NotificationPreference
    ).filter(
        NotificationPreference.user_id == user_id
    ).first()

    if not preferences:
        preferences = NotificationPreference(
            user_id=user_id,
            email_enabled=1,
            mobile_enabled=0,
            critical_alerts=1,
            high_risk_alerts=1
        )

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


@router.get("/preferences")
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preferences = get_or_create_preferences(
        db,
        current_user.id
    )

    return {
        "user_id": current_user.id,
        "email_enabled": bool(
            preferences.email_enabled
        ),
        "mobile_enabled": bool(
            preferences.mobile_enabled
        ),
        "critical_alerts": bool(
            preferences.critical_alerts
        ),
        "high_risk_alerts": bool(
            preferences.high_risk_alerts
        )
    }


@router.put("/preferences")
def update_preferences(
    data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preferences = get_or_create_preferences(
        db,
        current_user.id
    )

    preferences.email_enabled = int(
        data.email_enabled
    )

    preferences.mobile_enabled = int(
        data.mobile_enabled
    )

    preferences.critical_alerts = int(
        data.critical_alerts
    )

    preferences.high_risk_alerts = int(
        data.high_risk_alerts
    )

    db.commit()
    db.refresh(preferences)

    return {
        "message": "Notification preferences updated.",
        "email_enabled": bool(
            preferences.email_enabled
        ),
        "mobile_enabled": bool(
            preferences.mobile_enabled
        ),
        "critical_alerts": bool(
            preferences.critical_alerts
        ),
        "high_risk_alerts": bool(
            preferences.high_risk_alerts
        )
    }
