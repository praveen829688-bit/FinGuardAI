from sqlalchemy import Column, ForeignKey, Integer, String

from app.database.connection import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    category_type = Column(
        String(30),
        nullable=False
    )

    icon = Column(
        String(50),
        nullable=True
    )

    color = Column(
        String(20),
        nullable=True
    )
