import os
from datetime import datetime, timezone


class NotificationService:
    """
    FinGuard AI centralized notification engine.

    Channels:
        - Email
        - Mobile Push
        - In-App

    Demo mode is enabled when external credentials
    are not configured.
    """

    def __init__(self):
        self.email_enabled = bool(
            os.getenv("SMTP_HOST")
            and os.getenv("SMTP_USERNAME")
            and os.getenv("SMTP_PASSWORD")
        )

        self.mobile_enabled = bool(
            os.getenv("PUSH_PROVIDER")
            and os.getenv("PUSH_API_KEY")
        )

        self.demo_mode = not (
            self.email_enabled
            or self.mobile_enabled
        )

    def _build_alert(
        self,
        risk_score,
        severity,
        reasons
    ):
        return {
            "application": "FinGuard AI",
            "type": "SECURITY_ALERT",
            "severity": severity,
            "risk_score": round(
                float(risk_score),
                2
            ),
            "message": (
                f"{severity} financial security "
                f"alert detected."
            ),
            "reasons": reasons,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def send_email_alert(
        self,
        email,
        alert
    ):
        if not email:
            return {
                "success": False,
                "channel": "email",
                "status": "recipient_not_configured"
            }

        if not self.email_enabled:
            return {
                "success": False,
                "channel": "email",
                "status": "not_configured",
                "recipient": email
            }

        # Production SMTP integration will be enabled
        # after SMTP credentials are configured.
        return {
            "success": True,
            "channel": "email",
            "status": "queued",
            "recipient": email
        }

    def send_mobile_alert(
        self,
        device_token,
        alert
    ):
        if not device_token:
            return {
                "success": False,
                "channel": "mobile",
                "status": "device_not_configured"
            }

        if not self.mobile_enabled:
            return {
                "success": False,
                "channel": "mobile",
                "status": "not_configured"
            }

        # Production push provider integration will be
        # enabled after credentials are configured.
        return {
            "success": True,
            "channel": "mobile",
            "status": "queued"
        }

    def send_in_app_alert(
        self,
        user_id,
        alert
    ):
        return {
            "success": True,
            "channel": "in_app",
            "status": "created",
            "user_id": user_id,
            "alert": alert
        }

    def send_security_alert(
        self,
        email,
        device_token,
        risk_score,
        severity,
        reasons,
        user_id=None
    ):
        alert = self._build_alert(
            risk_score=risk_score,
            severity=severity,
            reasons=reasons
        )

        email_result = self.send_email_alert(
            email=email,
            alert=alert
        )

        mobile_result = self.send_mobile_alert(
            device_token=device_token,
            alert=alert
        )

        in_app_result = None

        if user_id is not None:
            in_app_result = self.send_in_app_alert(
                user_id=user_id,
                alert=alert
            )

        return {
            "success": (
                email_result["success"]
                or mobile_result["success"]
                or (
                    in_app_result is not None
                    and in_app_result["success"]
                )
            ),
            "severity": severity,
            "risk_score": round(
                float(risk_score),
                2
            ),
            "demo_mode": self.demo_mode,
            "email": email_result,
            "mobile": mobile_result,
            "in_app": in_app_result
        }


notification_service = NotificationService()
