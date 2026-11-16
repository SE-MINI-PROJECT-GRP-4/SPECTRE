from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.services.auth.passwords import (
    hash_password,
    verify_password,
)


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:
    """
    Create a new user account.

    Raises:
        ValueError: If the email is already registered.
    """

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise ValueError("Email is already registered.")

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.USER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """
    Authenticate a user using their email and password.

    Returns:
        User if authentication succeeds, otherwise None.
    """

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user