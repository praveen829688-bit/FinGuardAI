from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String
)

from app.database.connection import Base


class Bill(Base):

    __tablename__ = "bills"

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

    # Legacy database compatibility
    bill_name = Column(
        String(150),
        nullable=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    bill_type = Column(
        String(50),
        nullable=False,
        default="UTILITY"
    )

    provider = Column(
        String(150),
        nullable=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    due_date = Column(
        DateTime,
        nullable=False
    )

    frequency = Column(
        String(30),
        default="ONCE",
        nullable=False
    )

    status = Column(
        String(30),
        default="PENDING",
        nullable=False
    )

    auto_pay = Column(
        Integer,
        default=0,
        nullable=False
    )

    description = Column(
        String(500),
        nullable=True
    )

    last_paid_date = Column(
        DateTime,
        nullable=True
    )

    next_due_date = Column(
        DateTime,
        nullable=True
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
