from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from app.database.connection import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    security_event_id = Column(
        Integer,
        ForeignKey("security_events.id"),
        nullable=True,
        index=True
    )

    channel = Column(
        String(30),
        nullable=False
    )

    severity = Column(
        String(30),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    risk_score = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(30),
        default="created",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
