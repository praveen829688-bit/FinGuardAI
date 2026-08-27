from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database.connection import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=True
    )

    event_type = Column(
        String(50),
        nullable=False
    )

    severity = Column(
        String(30),
        nullable=False
    )

    risk_score = Column(
        Float,
        default=0.0
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        default="open"
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
