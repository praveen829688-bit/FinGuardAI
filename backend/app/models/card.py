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


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=True
    )

    card_type = Column(
        String(30),
        nullable=False
    )

    card_name = Column(
        String(100),
        nullable=False
    )

    last4 = Column(
        String(4),
        nullable=False
    )

    credit_limit = Column(
        Float,
        default=0.0
    )

    outstanding_amount = Column(
        Float,
        default=0.0
    )

    is_active = Column(
        Integer,
        default=1
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
