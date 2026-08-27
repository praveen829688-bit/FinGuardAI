from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from app.database.connection import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    account_name = Column(
        String(100),
        nullable=False
    )

    account_type = Column(
        String(50),
        nullable=False
    )

    institution_name = Column(
        String(100),
        nullable=True
    )

    account_number_last4 = Column(
        String(4),
        nullable=True
    )

    currency = Column(
        String(10),
        default="INR",
        nullable=False
    )

    balance = Column(
        Float,
        default=0.0,
        nullable=False
    )

    is_active = Column(
        Integer,
        default=1,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
