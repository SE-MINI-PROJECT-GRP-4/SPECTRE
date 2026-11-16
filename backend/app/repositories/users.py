from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    """
    Retrieve a user by their primary key.
    """

    return db.scalar(
        select(User).where(User.user_id == user_id)
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """
    Retrieve a user by email address.
    """

    return db.scalar(
        select(User).where(User.email == email)
    )