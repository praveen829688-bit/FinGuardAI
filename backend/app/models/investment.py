from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.connection import Base


class Investment(Base):
    __tablename__ = "investments"

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

    investment_type = Column(
        String(50),
        nullable=False
    )

    name = Column(
        String(150),
        nullable=False
    )

    platform = Column(
        String(100),
        nullable=True
    )

    invested_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    current_value = Column(
        Float,
        nullable=False,
        default=0
    )

    units = Column(
        Float,
        nullable=True
    )

    purchase_price = Column(
        Float,
        nullable=True
    )

    current_price = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="ACTIVE"
    )

    purchase_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
