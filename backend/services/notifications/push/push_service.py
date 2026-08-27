import os

from dotenv import load_dotenv


load_dotenv()


class PushNotificationService:

    def __init__(self):
        self.enabled = (
            os.getenv(
                "FIREBASE_ENABLED",
                "false"
            ).lower() == "true"
        )

        self.credentials_path = os.getenv(
            "FIREBASE_CREDENTIALS_PATH"
        )

        self.initialized = False

        if self.enabled:
            self._initialize()

    def _initialize(self):

        if not self.credentials_path:
            return

        if not os.path.exists(
            self.credentials_path
        ):
            return

        try:
            import firebase_admin
            from firebase_admin import credentials

            if not firebase_admin._apps:

                credential = (
                    credentials.Certificate(
                        self.credentials_path
                    )
                )

                firebase_admin.initialize_app(
                    credential
                )

            self.initialized = True

        except Exception:
            self.initialized = False

    def send_security_alert(
        self,
        device_token: str,
        risk_score: float,
        severity: str
    ):

        if not self.initialized:

            return {
                "success": False,
                "status": "not_configured"
            }

        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=(
                        f"FinGuard AI: {severity} Alert"
                    ),
                    body=(
                        f"Suspicious transaction detected. "
                        f"Risk score: {risk_score}/100"
                    )
                ),
                token=device_token
            )

            response = messaging.send(
                message
            )

            return {
                "success": True,
                "status": "sent",
                "message_id": response
            }

        except Exception as exc:

            return {
                "success": False,
                "status": "failed",
                "error": str(exc)
            }


push_notification_service = (
    PushNotificationService()
)
