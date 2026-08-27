from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.connection import Base


class Debt(Base):
    __tablename__ = "debts"

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

    debt_name = Column(
        String(150),
        nullable=False
    )

    debt_type = Column(
        String(50),
        nullable=False
    )

    lender = Column(
        String(150),
        nullable=True
    )

    principal_amount = Column(
        Float,
        nullable=False
    )

    outstanding_amount = Column(
        Float,
        nullable=False
    )

    interest_rate = Column(
        Float,
        default=0.0,
        nullable=False
    )

    minimum_payment = Column(
        Float,
        default=0.0,
        nullable=False
    )

    due_date = Column(
        DateTime,
        nullable=True
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
