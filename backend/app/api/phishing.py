from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.security_event import SecurityEvent
from app.models.user import User

from ml.phishing_detection.phishing_service import (
    phishing_service
)


router = APIRouter(
    prefix="/api/phishing",
    tags=["Phishing Protection"]
)


class URLScanRequest(BaseModel):
    url: str = Field(
        min_length=4,
        max_length=2048
    )


@router.post("/scan")
def scan_url(
    data: URLScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = phishing_service.analyze(
        data.url
    )

    if result["risk_score"] >= 40:

        event = SecurityEvent(
            user_id=current_user.id,
            event_type="PHISHING_URL",
            severity=result["status"],
            risk_score=result["risk_score"],
            title="Potential phishing URL detected",
            description="; ".join(
                result["indicators"]
            ),
            status="open"
        )

        db.add(event)
        db.commit()

        result["security_event_created"] = True

    else:
        result["security_event_created"] = False

    return result
