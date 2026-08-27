import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


class EmailAlertService:

    def __init__(self):
        self.host = os.getenv(
            "SMTP_HOST",
            "smtp.gmail.com"
        )

        self.port = int(
            os.getenv(
                "SMTP_PORT",
                "587"
            )
        )

        self.username = os.getenv(
            "SMTP_USERNAME"
        )

        self.password = os.getenv(
            "SMTP_PASSWORD"
        )

        self.from_email = os.getenv(
            "ALERT_FROM_EMAIL"
        )

    def is_configured(self):
        return all([
            self.username,
            self.password,
            self.from_email
        ])

    def send_security_alert(
        self,
        recipient: str,
        risk_score: float,
        severity: str,
        reasons: list[str]
    ):

        if not self.is_configured():
            return {
                "success": False,
                "status": "not_configured"
            }

        message = EmailMessage()

        message["Subject"] = (
            f"FinGuard AI Security Alert - {severity}"
        )

        message["From"] = self.from_email
        message["To"] = recipient

        reason_text = "\n".join(
            f"- {reason}"
            for reason in reasons
        )

        message.set_content(
            f"""
FinGuard AI Security Alert

A potentially suspicious financial transaction
has been detected.

Risk Score: {risk_score}/100
Severity: {severity}

Security Indicators:
{reason_text}

Please review your FinGuard AI security dashboard.

If you did not authorize this activity, contact
your financial institution immediately.

FinGuard AI
Financial Intelligence & Security Platform
"""
        )

        try:
            with smtplib.SMTP(
                self.host,
                self.port
            ) as server:

                server.starttls()

                server.login(
                    self.username,
                    self.password
                )

                server.send_message(message)

            return {
                "success": True,
                "status": "sent"
            }

        except Exception as exc:

            return {
                "success": False,
                "status": "failed",
                "error": str(exc)
            }


email_alert_service = EmailAlertService()
