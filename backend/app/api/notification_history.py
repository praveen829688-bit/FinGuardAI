from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.notification import Notification
from app.models.user import User


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


def serialize_notification(notification):
    return {
        "id": notification.id,
        "channel": notification.channel,
        "severity": notification.severity,
        "title": notification.title,
        "message": notification.message,
        "risk_score": (
            round(float(notification.risk_score), 2)
            if notification.risk_score is not None
            else None
        ),
        "status": notification.status,
        "security_event_id": notification.security_event_id,
        "created_at": (
            notification.created_at.isoformat()
            if notification.created_at
            else None
        )
    }


@router.get("/history")
def notification_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(
        Notification
    ).filter(
        Notification.user_id == current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).limit(100).all()

    return {
        "count": len(notifications),
        "notifications": [
            serialize_notification(notification)
            for notification in notifications
        ]
    }


@router.get("/unread")
def unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(
        Notification
    ).filter(
        Notification.user_id == current_user.id,
        Notification.status == "created"
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return {
        "count": len(notifications),
        "notifications": [
            serialize_notification(notification)
            for notification in notifications
        ]
    }


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(
        Notification
    ).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found."
        )

    notification.status = "read"

    db.commit()
    db.refresh(notification)

    return {
        "success": True,
        "message": "Notification marked as read.",
        "notification": serialize_notification(
            notification
        )
    }


@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(
        Notification
    ).filter(
        Notification.user_id == current_user.id,
        Notification.status == "created"
    ).all()

    for notification in notifications:
        notification.status = "read"

    db.commit()

    return {
        "success": True,
        "updated": len(notifications)
    }
