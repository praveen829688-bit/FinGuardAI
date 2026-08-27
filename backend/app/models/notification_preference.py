from sqlalchemy import Column, ForeignKey, Integer

from app.database.connection import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )

    email_enabled = Column(
        Integer,
        default=1,
        nullable=False
    )

    mobile_enabled = Column(
        Integer,
        default=0,
        nullable=False
    )

    critical_alerts = Column(
        Integer,
        default=1,
        nullable=False
    )

    high_risk_alerts = Column(
        Integer,
        default=1,
        nullable=False
    )
