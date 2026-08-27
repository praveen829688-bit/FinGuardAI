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


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False,
        index=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True
    )

    transaction_type = Column(
        String(30),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    currency = Column(
        String(10),
        default="INR",
        nullable=False
    )

    merchant_name = Column(
        String(150),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    location = Column(
        String(150),
        nullable=True
    )

    device_id = Column(
        String(150),
        nullable=True
    )

    ip_address = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(30),
        default="completed",
        nullable=False
    )

    fraud_risk_score = Column(
        Float,
        default=0.0,
        nullable=False
    )

    fraud_status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
