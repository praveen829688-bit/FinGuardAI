from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.security_event import SecurityEvent
from app.models.user import User


router = APIRouter(
    prefix="/api/security",
    tags=["Security Center"]
)


@router.get("/events")
def get_security_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    events = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == current_user.id
    ).order_by(
        SecurityEvent.created_at.desc()
    ).all()

    return events


@router.get("/events/{event_id}")
def get_security_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(SecurityEvent).filter(
        SecurityEvent.id == event_id,
        SecurityEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Security event not found."
        )

    return event


@router.patch("/events/{event_id}/resolve")
def resolve_security_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(SecurityEvent).filter(
        SecurityEvent.id == event_id,
        SecurityEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Security event not found."
        )

    event.status = "resolved"

    db.commit()
    db.refresh(event)

    return {
        "message": "Security event resolved successfully.",
        "event_id": event.id,
        "status": event.status
    }
