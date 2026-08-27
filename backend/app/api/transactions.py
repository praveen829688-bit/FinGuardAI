import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.account import Account
from app.models.notification_preference import (
    NotificationPreference
)
from app.models.security_event import SecurityEvent
from app.models.transaction import Transaction
from app.models.user import User

from ml.fraud_detection.service import risk_service

from services.notifications.notification_service import (
    notification_service
)

from services.notifications.notification_persistence import (
    notification_persistence_service
)


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"]
)


class TransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None

    transaction_type: str = Field(
        min_length=3,
        max_length=30
    )

    amount: float = Field(gt=0)

    merchant_name: str | None = None
    description: str | None = None
    location: str | None = None
    device_id: str | None = None
    ip_address: str | None = None

    previous_average: float = Field(
        default=1000.0,
        gt=0
    )

    new_device: bool = False
    unusual_location: bool = False


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # ACCOUNT VALIDATION
    # ========================================================

    account = db.query(Account).filter(
        Account.id == data.account_id,
        Account.user_id == current_user.id,
        Account.is_active == 1
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Financial account not found."
        )

    # ========================================================
    # REAL-TIME CONTEXT
    # ========================================================

    current_hour = datetime.now().hour

    night_transaction = (
        current_hour < 6
        or current_hour >= 23
    )

    amount_ratio = (
        data.amount / data.previous_average
    )

    # ========================================================
    # AI RISK ENGINE
    # ========================================================

    ai_result = risk_service.analyze(
        amount=data.amount,
        amount_ratio=amount_ratio,
        new_device=data.new_device,
        unusual_location=data.unusual_location,
        night_transaction=night_transaction,
        transaction_type=data.transaction_type
    )

    # ========================================================
    # SAVE TRANSACTION
    # ========================================================

    transaction = Transaction(
        transaction_reference=(
            f"FG-{uuid.uuid4().hex[:16].upper()}"
        ),
        user_id=current_user.id,
        account_id=data.account_id,
        category_id=data.category_id,
        transaction_type=data.transaction_type,
        amount=data.amount,
        merchant_name=data.merchant_name,
        description=data.description,
        location=data.location,
        device_id=data.device_id,
        ip_address=data.ip_address,
        status="completed",
        fraud_risk_score=ai_result["risk_score"],
        fraud_status=ai_result["status"]
    )

    db.add(transaction)
    db.flush()

    notification_result = None
    persistent_notifications = []

    # ========================================================
    # SECURITY EVENT + NOTIFICATION PIPELINE
    # ========================================================

    if ai_result["risk_score"] >= 60:

        security_event = SecurityEvent(
            user_id=current_user.id,
            transaction_id=transaction.id,
            event_type="TRANSACTION_RISK",
            severity=ai_result["status"],
            risk_score=ai_result["risk_score"],
            title="Suspicious transaction detected",
            description="; ".join(
                ai_result["reasons"]
            ),
            status="open"
        )

        db.add(security_event)
        db.flush()

        # ----------------------------------------------------
        # Notification preferences
        # ----------------------------------------------------

        preferences = db.query(
            NotificationPreference
        ).filter(
            NotificationPreference.user_id
            == current_user.id
        ).first()

        if not preferences:

            preferences = NotificationPreference(
                user_id=current_user.id,
                email_enabled=1,
                mobile_enabled=0,
                critical_alerts=1,
                high_risk_alerts=1
            )

            db.add(preferences)
            db.flush()

        # ----------------------------------------------------
        # Determine whether this severity should alert
        # ----------------------------------------------------

        should_alert = (
            (
                ai_result["status"] == "CRITICAL"
                and bool(preferences.critical_alerts)
            )
            or
            (
                ai_result["status"] == "HIGH_RISK"
                and bool(preferences.high_risk_alerts)
            )
        )

        if should_alert:

            email = (
                current_user.email
                if preferences.email_enabled
                else None
            )

            # ------------------------------------------------
            # External notification service
            # ------------------------------------------------

            notification_result = (
                notification_service.send_security_alert(
                    email=email,
                    device_token=None,
                    risk_score=ai_result["risk_score"],
                    severity=ai_result["status"],
                    reasons=ai_result["reasons"],
                    user_id=current_user.id
                )
            )

            # ------------------------------------------------
            # Persistent notifications
            # ------------------------------------------------

            persistent_notifications = (
                notification_persistence_service
                .create_security_notifications(
                    db=db,
                    user_id=current_user.id,
                    security_event_id=security_event.id,
                    severity=ai_result["status"],
                    risk_score=ai_result["risk_score"],
                    reasons=ai_result["reasons"],
                    email_enabled=bool(
                        preferences.email_enabled
                    ),
                    mobile_enabled=bool(
                        preferences.mobile_enabled
                    )
                )
            )

    # ========================================================
    # COMMIT EVERYTHING TOGETHER
    # ========================================================

    db.commit()
    db.refresh(transaction)

    return {
        "transaction": transaction,
        "ai_security_analysis": ai_result,
        "notification": notification_result,
        "persistent_notifications": [
            {
                "id": item.id,
                "channel": item.channel,
                "severity": item.severity,
                "status": item.status,
                "security_event_id": (
                    item.security_event_id
                )
            }
            for item in persistent_notifications
        ]
    }


@router.get("/")
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(
        Transaction.created_at.desc()
    ).all()


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found."
        )

    return transaction
