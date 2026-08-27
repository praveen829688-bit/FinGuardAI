from app.models.notification import Notification


class NotificationPersistenceService:
    """
    Stores every FinGuard AI security notification
    in the database.

    Channels:
        IN_APP
        EMAIL
        MOBILE
    """

    def create_notification(
        self,
        db,
        user_id,
        security_event_id,
        channel,
        severity,
        title,
        message,
        risk_score,
        status="created"
    ):
        notification = Notification(
            user_id=user_id,
            security_event_id=security_event_id,
            channel=channel,
            severity=severity,
            title=title,
            message=message,
            risk_score=float(risk_score),
            status=status
        )

        db.add(notification)

        return notification

    def create_security_notifications(
        self,
        db,
        user_id,
        security_event_id,
        severity,
        risk_score,
        reasons,
        email_enabled=True,
        mobile_enabled=False
    ):
        title = (
            "Critical financial security alert"
            if severity == "CRITICAL"
            else "High-risk financial security alert"
        )

        message = (
            "FinGuard AI detected a suspicious financial "
            "transaction. Reasons: "
            + "; ".join(reasons)
        )

        notifications = []

        # ----------------------------------------------------
        # IN-APP notification
        # ----------------------------------------------------

        notifications.append(
            self.create_notification(
                db=db,
                user_id=user_id,
                security_event_id=security_event_id,
                channel="IN_APP",
                severity=severity,
                title=title,
                message=message,
                risk_score=risk_score,
                status="created"
            )
        )

        # ----------------------------------------------------
        # EMAIL notification
        # ----------------------------------------------------

        if email_enabled:
            notifications.append(
                self.create_notification(
                    db=db,
                    user_id=user_id,
                    security_event_id=security_event_id,
                    channel="EMAIL",
                    severity=severity,
                    title=title,
                    message=message,
                    risk_score=risk_score,
                    status="pending"
                )
            )

        # ----------------------------------------------------
        # MOBILE notification
        # ----------------------------------------------------

        if mobile_enabled:
            notifications.append(
                self.create_notification(
                    db=db,
                    user_id=user_id,
                    security_event_id=security_event_id,
                    channel="MOBILE",
                    severity=severity,
                    title=title,
                    message=message,
                    risk_score=risk_score,
                    status="pending"
                )
            )

        return notifications


notification_persistence_service = (
    NotificationPersistenceService()
)
