from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.connection import get_db
from app.models.category import Category
from app.models.user import User


router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"]
)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category_type: str = Field(
        min_length=3,
        max_length=30
    )
    icon: str | None = None
    color: str | None = None


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = Category(
        user_id=current_user.id,
        name=data.name,
        category_type=data.category_type,
        icon=data.icon,
        color=data.color
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("/")
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Category).filter(
        (Category.user_id == current_user.id)
        | (Category.user_id.is_(None))
    ).all()
