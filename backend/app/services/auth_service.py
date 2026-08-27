from sqlalchemy.orm import Session

from app.models.user import User
from app.security.password import hash_password, verify_password


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    full_name: str,
    email: str,
    password: str
):
    existing_user = get_user_by_email(db, email)

    if existing_user:
        return None

    user = User(
        full_name=full_name,
        email=email.lower(),
        password_hash=hash_password(password),
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
