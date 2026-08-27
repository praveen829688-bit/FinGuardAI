from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.connection import Base


class CreditCard(Base):
    __tablename__ = "credit_cards"

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

    card_name = Column(
        String(150),
        nullable=False
    )

    issuer = Column(
        String(100),
        nullable=True
    )

    last4 = Column(
        String(4),
        nullable=True
    )

    credit_limit = Column(
        Float,
        nullable=False
    )

    outstanding_balance = Column(
        Float,
        default=0.0,
        nullable=False
    )

    available_credit = Column(
        Float,
        default=0.0,
        nullable=False
    )

    utilization_percentage = Column(
        Float,
        default=0.0,
        nullable=False
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    minimum_due = Column(
        Float,
        default=0.0,
        nullable=False
    )

    interest_rate = Column(
        Float,
        default=0.0,
        nullable=False
    )

    status = Column(
        String(30),
        default="ACTIVE",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
